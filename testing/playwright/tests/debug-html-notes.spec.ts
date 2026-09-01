import { test, expect } from '../fixtures/auth.fixture';

function generateMockNotes() {
  return [
    { note_id: 'HTML-MED-001', title: 'Emergency OSCE Notes - Anaphylaxis Management', specialty: 'Medicine', category: 'Emergency', file_size_kb: 16, estimated_reading_minutes: 6, topics: ['Anaphylaxis', 'Emergency Management', 'ABCDE Approach'], preview_text: 'Emergency OSCE Notes - Anaphylaxis Management...', file_path: 'Medicine/01_Emergency_Anaphylaxis_Management.html', related_osce_ids: [], created_at: '2026-05-28T07:01:45.123Z' },
    { note_id: 'HTML-MED-002', title: 'History Taking - Chest Pain', specialty: 'Medicine', category: 'History', file_size_kb: 12, estimated_reading_minutes: 5, topics: ['Chest Pain', 'History Taking', 'Cardiology'], preview_text: 'Comprehensive guide...', file_path: 'Medicine/02_History_Chest_Pain.html', related_osce_ids: [], created_at: '2026-05-28T07:01:45.123Z' },
    { note_id: 'HTML-SURG-001', title: 'Pre-operative Assessment', specialty: 'Surgery', category: 'Physical Examination', file_size_kb: 14, estimated_reading_minutes: 7, topics: ['Pre-op', 'Assessment', 'Surgery'], preview_text: 'Pre-operative assessment...', file_path: 'Surgery/01_Preoperative_Assessment.html', related_osce_ids: [], created_at: '2026-05-28T07:01:45.123Z' },
    { note_id: 'HTML-PSY-001', title: 'Mental State Examination', specialty: 'Psychiatry', category: 'Examination', file_size_kb: 18, estimated_reading_minutes: 8, topics: ['MSE', 'Psychiatry', 'Examination'], preview_text: 'Structured approach...', file_path: 'Psychiatry/01_Mental_State_Examination.html', related_osce_ids: [], created_at: '2026-05-28T07:01:45.123Z' },
  ];
}

async function setupHTMLNotesApiMock(page: import('@playwright/test').Page) {
  await page.route('**/api/v1/html-notes/**', async (route, request) => {
    const url = request.url();
    if (url.includes('/specialties/list')) {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([{ specialty: 'Medicine', count: 18 }, { specialty: 'Mock OSCE Stations', count: 19 }, { specialty: 'Ethics & Communication', count: 6 }, { specialty: 'Surgery', count: 5 }, { specialty: 'Psychiatry', count: 5 }, { specialty: 'Paediatrics', count: 5 }, { specialty: 'Obstetrics & Gynecology', count: 5 }]) });
      return;
    }
    if (url.includes('/by-specialty/')) {
      const specialty = decodeURIComponent(url.split('/by-specialty/')[1].split('?')[0]);
      const notes = generateMockNotes().filter(n => n.specialty === specialty);
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(notes) });
      return;
    }
    if (url.includes('/content')) {
      const noteId = url.split('/html-notes/')[1]?.split('/')[0];
      await route.fulfill({ status: 200, contentType: 'text/html', body: `<html><head><title>Note ${noteId}</title></head><body><h1>Emergency OSCE Notes</h1><p>Test content for ${noteId}</p></body></html>` });
      return;
    }
    const singleNoteMatch = url.match(/\/html-notes\/([^/]+)$/);
    if (singleNoteMatch) {
      const noteId = singleNoteMatch[1];
      const note = generateMockNotes().find(n => n.note_id === noteId) || generateMockNotes()[0];
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(note) });
      return;
    }
    const urlObj = new URL(url);
    const specialty = urlObj.searchParams.get('specialty') || undefined;
    const category = urlObj.searchParams.get('category') || undefined;
    let notes = generateMockNotes();
    if (specialty) notes = notes.filter(n => n.specialty === specialty);
    if (category) notes = notes.filter(n => n.category === category);
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(notes) });
  });
}

test('exact full mock', async ({ studentPage: page }) => {
  page.on('pageerror', err => console.log('PAGE ERROR:', err.message));

  await setupHTMLNotesApiMock(page);
  await page.goto('/html-notes');
  await page.waitForTimeout(5000);

  const heading = page.locator('h1');
  console.log('H1 COUNT:', await heading.count());
  console.log('H1 TEXT:', await heading.textContent().catch(() => 'N/A'));

  await expect(heading).toBeVisible({ timeout: 10000 });
});
