import { setupServer } from 'msw/node';
import { handlers } from './mocks/handlers';

const server = setupServer(...handlers);

export default async function globalSetup() {
  console.log('Starting MSW server for API mocking...');
  server.listen({ 
    onUnhandledRequest: 'bypass',
  });
  
  return async () => {
    console.log('Stopping MSW server...');
    server.close();
  };
}
