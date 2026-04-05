#!/usr/bin/env node
/**
 * Playwright MCP Server
 *
 * Exposes Playwright test execution to Claude via Model Context Protocol
 * Enables autonomous testing where Claude monitors tests and fixes errors
 *
 * Features:
 * - Real-time test execution monitoring
 * - Failure detection with screenshots
 * - Test result streaming
 * - Re-run capabilities
 *
 * Usage:
 *   npm run mcp:server
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { spawn, ChildProcess } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';

interface TestResult {
  testFile: string;
  testName: string;
  status: 'passed' | 'failed' | 'skipped';
  duration: number;
  error?: string;
  screenshot?: string;
  trace?: string;
}

interface TestSession {
  sessionId: string;
  startTime: Date;
  tests: TestResult[];
  process: ChildProcess | null;
  status: 'running' | 'completed' | 'failed';
}

class PlaywrightMCPServer {
  private server: Server;
  private currentSession: TestSession | null = null;
  private testResults: TestResult[] = [];

  constructor() {
    this.server = new Server(
      {
        name: 'playwright-mcp-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupHandlers();
  }

  private setupHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'run_tests',
          description: 'Run Playwright tests in headed mode with live monitoring',
          inputSchema: {
            type: 'object',
            properties: {
              testFile: {
                type: 'string',
                description: 'Specific test file to run (optional, runs all if not provided)',
              },
              grep: {
                type: 'string',
                description: 'Filter tests by name pattern (optional)',
              },
              headed: {
                type: 'boolean',
                description: 'Run in headed mode (visible browser)',
                default: true,
              },
              debug: {
                type: 'boolean',
                description: 'Run in debug mode with inspector',
                default: false,
              },
            },
          },
        },
        {
          name: 'get_test_results',
          description: 'Get results from the current or last test session',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        },
        {
          name: 'get_failure_details',
          description: 'Get detailed information about test failures including screenshots',
          inputSchema: {
            type: 'object',
            properties: {
              testName: {
                type: 'string',
                description: 'Name of the failed test',
              },
            },
          },
        },
        {
          name: 'rerun_failed_tests',
          description: 'Re-run only the tests that failed in the last session',
          inputSchema: {
            type: 'object',
            properties: {
              headed: {
                type: 'boolean',
                description: 'Run in headed mode',
                default: true,
              },
            },
          },
        },
        {
          name: 'stop_tests',
          description: 'Stop the currently running test session',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        },
      ],
    }));

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      switch (name) {
        case 'run_tests':
          return await this.runTests(args);
        case 'get_test_results':
          return await this.getTestResults();
        case 'get_failure_details':
          return await this.getFailureDetails(args.testName as string);
        case 'rerun_failed_tests':
          return await this.rerunFailedTests(args);
        case 'stop_tests':
          return await this.stopTests();
        default:
          throw new Error(`Unknown tool: ${name}`);
      }
    });
  }

  private async runTests(args: any) {
    const { testFile, grep, headed = true, debug = false } = args;

    // Create new session
    this.currentSession = {
      sessionId: `session_${Date.now()}`,
      startTime: new Date(),
      tests: [],
      process: null,
      status: 'running',
    };

    // Build Playwright command
    const playwrightArgs = ['test'];

    if (testFile) {
      playwrightArgs.push(testFile);
    }

    if (grep) {
      playwrightArgs.push('--grep', grep);
    }

    if (headed) {
      playwrightArgs.push('--headed');
    }

    if (debug) {
      playwrightArgs.push('--debug');
    }

    // Add reporter for JSON output
    playwrightArgs.push('--reporter=json');

    return new Promise((resolve, reject) => {
      // Spawn Playwright process
      const process = spawn('npx', ['playwright', ...playwrightArgs], {
        cwd: path.join(__dirname, '..'),
        stdio: ['inherit', 'pipe', 'pipe'],
      });

      this.currentSession.process = process;

      let stdoutData = '';
      let stderrData = '';

      process.stdout?.on('data', (data) => {
        stdoutData += data.toString();
        // Parse JSON results in real-time
        this.parseTestResults(stdoutData);
      });

      process.stderr?.on('data', (data) => {
        stderrData += data.toString();
      });

      process.on('close', (code) => {
        if (this.currentSession) {
          this.currentSession.status = code === 0 ? 'completed' : 'failed';
        }

        const results = this.parseTestResults(stdoutData);
        this.testResults = results;

        resolve({
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                sessionId: this.currentSession?.sessionId,
                status: this.currentSession?.status,
                exitCode: code,
                totalTests: results.length,
                passed: results.filter((t) => t.status === 'passed').length,
                failed: results.filter((t) => t.status === 'failed').length,
                skipped: results.filter((t) => t.status === 'skipped').length,
                results: results,
              }, null, 2),
            },
          ],
        });
      });

      process.on('error', (error) => {
        reject({
          content: [
            {
              type: 'text',
              text: `Failed to start Playwright: ${error.message}`,
            },
          ],
        });
      });
    });
  }

  private parseTestResults(jsonOutput: string): TestResult[] {
    try {
      // Find JSON in output
      const jsonMatch = jsonOutput.match(/\{[\s\S]*"suites"[\s\S]*\}/);
      if (!jsonMatch) return [];

      const report = JSON.parse(jsonMatch[0]);
      const results: TestResult[] = [];

      // Parse test results from Playwright JSON reporter format
      report.suites?.forEach((suite: any) => {
        suite.specs?.forEach((spec: any) => {
          spec.tests?.forEach((test: any) => {
            const result: TestResult = {
              testFile: suite.file || '',
              testName: test.title || '',
              status: test.status || 'skipped',
              duration: test.duration || 0,
            };

            // Add error details if failed
            if (test.status === 'failed' && test.results?.[0]?.error) {
              result.error = test.results[0].error.message;
            }

            // Add screenshot path if available
            if (test.results?.[0]?.attachments) {
              const screenshot = test.results[0].attachments.find(
                (a: any) => a.name === 'screenshot'
              );
              if (screenshot) {
                result.screenshot = screenshot.path;
              }

              const trace = test.results[0].attachments.find(
                (a: any) => a.name === 'trace'
              );
              if (trace) {
                result.trace = trace.path;
              }
            }

            results.push(result);
          });
        });
      });

      return results;
    } catch (error) {
      console.error('Failed to parse test results:', error);
      return [];
    }
  }

  private async getTestResults() {
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            sessionId: this.currentSession?.sessionId,
            status: this.currentSession?.status,
            totalTests: this.testResults.length,
            passed: this.testResults.filter((t) => t.status === 'passed').length,
            failed: this.testResults.filter((t) => t.status === 'failed').length,
            skipped: this.testResults.filter((t) => t.status === 'skipped').length,
            results: this.testResults,
          }, null, 2),
        },
      ],
    };
  }

  private async getFailureDetails(testName: string) {
    const failedTests = this.testResults.filter(
      (t) => t.status === 'failed' && (!testName || t.testName.includes(testName))
    );

    const details = await Promise.all(
      failedTests.map(async (test) => {
        let screenshotData: string | null = null;

        // Read screenshot if available
        if (test.screenshot && fs.existsSync(test.screenshot)) {
          screenshotData = fs.readFileSync(test.screenshot, 'base64');
        }

        return {
          testFile: test.testFile,
          testName: test.testName,
          error: test.error,
          screenshot: screenshotData ? `data:image/png;base64,${screenshotData}` : null,
          trace: test.trace,
        };
      })
    );

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            failedCount: failedTests.length,
            failures: details,
          }, null, 2),
        },
      ],
    };
  }

  private async rerunFailedTests(args: any) {
    const failedTests = this.testResults.filter((t) => t.status === 'failed');

    if (failedTests.length === 0) {
      return {
        content: [
          {
            type: 'text',
            text: 'No failed tests to re-run',
          },
        ],
      };
    }

    // Build grep pattern to match failed tests
    const testNames = failedTests.map((t) => t.testName).join('|');
    return await this.runTests({
      grep: testNames,
      headed: args.headed ?? true,
    });
  }

  private async stopTests() {
    if (this.currentSession?.process) {
      this.currentSession.process.kill();
      this.currentSession.status = 'failed';

      return {
        content: [
          {
            type: 'text',
            text: `Stopped test session: ${this.currentSession.sessionId}`,
          },
        ],
      };
    }

    return {
      content: [
        {
          type: 'text',
          text: 'No active test session to stop',
        },
      ],
    };
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Playwright MCP Server running on stdio');
  }
}

// Start server
const server = new PlaywrightMCPServer();
server.run().catch(console.error);
