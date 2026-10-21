/* The HTML remains readable without JavaScript. Check that its snapshot matches JSON. */
'use strict';
const snapshotStatus = document.getElementById('snapshot-status');
fetch('data/opd-progress.json', { cache: 'no-cache' })
  .then(response => {
    if (!response.ok) throw new Error('Progress snapshot unavailable');
    return response.json();
  })
  .then(snapshot => {
    if (snapshot.schema_version !== 1 || snapshot.snapshot_utc !== snapshotStatus.dataset.snapshot) {
      throw new Error('Page and progress JSON are from different snapshots');
    }
    document.documentElement.dataset.snapshotCheck = 'passed';
  })
  .catch(error => {
    snapshotStatus.textContent = `${snapshotStatus.textContent} · ${error.message}. Open the progress JSON to check the current record.`;
    snapshotStatus.classList.add('error');
    document.documentElement.dataset.snapshotCheck = 'failed';
  });
