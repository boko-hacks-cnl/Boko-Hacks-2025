
function initializeApp() {
    console.log('Notes app initialization started');

    attachEventHandlers();
}

function attachEventHandlers() {
    console.log('Attaching event handlers');

    const form = document.getElementById('note-form');
    if (form) {
        console.log('Found note form, attaching submit handler');
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            console.log('Form submitted');
            saveNote();
        });
    } else {
        console.error('Note form not found');
    }

    const searchButton = document.getElementById('search-button');
    if (searchButton) {
        console.log('Found search button, attaching click handler');
        searchButton.addEventListener('click', function() {
            console.log('Search button clicked');
            searchNotes();
        });
    } else {
        console.error('Search button not found');
    }

    document.querySelectorAll('.delete-note').forEach(button => {
        button.addEventListener('click', function() {
            const noteId = this.getAttribute('data-note-id');
            deleteNote(noteId);
        });
    });
}

function showMessage(type, message) {
    const messageArea = document.getElementById('message-area');
    if (!messageArea) return;

    const messageElement = document.createElement('div');
    messageElement.className = `message ${type}-message`;
    messageElement.textContent = message;

    messageArea.appendChild(messageElement);

    setTimeout(() => void messageElement.remove(), 5000);
}

function saveNote() {
    console.log('Saving note...');

    const titleInput = document.querySelector('input[name="title"]');
    const contentInput = document.querySelector('textarea[name="content"]');

    if (!titleInput || !contentInput) {
        console.error('Cannot find title or content inputs');
        showMessage('error', 'Form inputs not found');
        return;
    }

    const title = titleInput.value.trim();
    const content = contentInput.value.trim();

    console.log('Title:', title);
    console.log('Content:', content);

    const formData = new FormData();
    formData.append('title', title);
    formData.append('content', content);

    fetch('/apps/notes/create', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        console.log('Response status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Save response:', data);

        if (data.success) {
            console.log('Note saved successfully');
            titleInput.value = '';
            contentInput.value = '';

            const notesList = document.getElementById('notes-list');
            const note = data.note;
            
            const noteElement = document.createElement('div');
            noteElement.className = 'note-card';
            
            const titleEl = document.createElement('h3');
            titleEl.textContent = note.title;
            
            const contentEl = document.createElement('div');
            contentEl.className = 'note-content';
            contentEl.textContent = note.content;
            
            const metaEl = document.createElement('div');
            metaEl.className = 'note-meta';
            metaEl.textContent = `ID: ${note.id} | Created: ${note.created_at} `;
            
            const deleteBtn = document.createElement('button');
            deleteBtn.type = 'button';
            deleteBtn.className = 'delete-note';
            deleteBtn.textContent = 'Delete';
            deleteBtn.setAttribute('data-note-id', note.id);
            
            metaEl.appendChild(deleteBtn);
            noteElement.appendChild(titleEl);
            noteElement.appendChild(contentEl);
            noteElement.appendChild(metaEl);
            
            notesList.insertBefore(noteElement, notesList.firstChild);
            
            deleteBtn.addEventListener('click', function() {
                deleteNote(note.id);
            });

            showMessage('success', 'Note saved successfully');
        } else {
            console.error('Error saving note:', data.error || 'Unknown error');
            showMessage('error', `Error saving note: ${data.error || 'Unknown error'}`);
        }
    })
    .catch(error => {
        console.error('Fetch error:', error);
        showMessage('error', `Error saving note: ${error.message}`);
    });
}

function searchNotes() {
    const query = document.getElementById('search')?.value.trim() || '';
    console.log('Searching for:', query);

    fetch(`/apps/notes/search?q=${encodeURIComponent(query)}`)
    .then(response => {
        console.log('Search response status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Search results:', data);

        const notesList = document.getElementById('notes-list');
        if (!notesList) {
            console.error('Notes list element not found');
            return;
        }

        if (data.success && Array.isArray(data.notes)) {
            console.log(`Found ${data.notes.length} notes matching query`);

            if (data.notes.length === 0) {
                notesList.innerHTML = '<div class="note-card"><p>No notes found matching your search.</p></div>';
                showMessage('info', 'No notes found matching your search');
                return;
            }

            notesList.innerHTML = '';
            data.notes.forEach(note => {
                const noteElement = document.createElement('div');
                noteElement.className = 'note-card';
                
                const titleEl = document.createElement('h3');
                titleEl.textContent = note.title;
                
                const contentEl = document.createElement('div');
                contentEl.className = 'note-content';
                contentEl.textContent = note.content;
                
                const metaEl = document.createElement('div');
                metaEl.className = 'note-meta';
                metaEl.textContent = `ID: ${note.id} | Created: ${note.created_at} `;
                
                const deleteBtn = document.createElement('button');
                deleteBtn.type = 'button';
                deleteBtn.className = 'delete-note';
                deleteBtn.textContent = 'Delete';
                deleteBtn.setAttribute('data-note-id', note.id);
                
                metaEl.appendChild(deleteBtn);
                noteElement.appendChild(titleEl);
                noteElement.appendChild(contentEl);
                noteElement.appendChild(metaEl);
                
                notesList.appendChild(noteElement);
                
                deleteBtn.addEventListener('click', function() {
                    deleteNote(note.id);
                });
            });

            showMessage('success', `Found ${data.notes.length} notes matching your search`);
        } else {
            console.error('Search failed or returned invalid data');
            notesList.innerHTML = '<div class="note-card"><p>An error occurred while searching notes.</p></div>';
            showMessage('error', `Search failed: ${data.error || 'Unknown error'}`);
        }
    })
    .catch(error => {
        console.error('Search fetch error:', error);
        const notesList = document.getElementById('notes-list');
        if (notesList) {
            notesList.innerHTML = '<div class="note-card"><p>An error occurred while searching notes.</p></div>';
        }
        showMessage('error', `Search error: ${error.message}`);
    });
}

function deleteNote(noteId) {
    if (confirm('Are you sure you want to delete this note?')) {
        console.log('Deleting note:', noteId);

        fetch(`/apps/notes/delete/${encodeURIComponent(noteId)}`, {
            method: 'DELETE'
        })
        .then(response => {
            console.log('Delete response status:', response.status);

            if (response.status === 404) {
                throw new Error('Note not found');
            }
            return response.json();
        })
        .then(data => {
            console.log('Delete response data:', data);

            if (data.success) {
                console.log('Note deleted successfully');

                const deleteBtn = document.querySelector(`.delete-btn[data-note-id="${noteId}"]`);
                if (deleteBtn) {
                    const noteElement = deleteBtn.closest('.note-card');
                    if (noteElement) {
                        noteElement.remove();
                    } else {
                        console.error('Note element not found');
                        showMessage('error', 'Note element not found');
                    }
                } else {
                    const notes = document.querySelectorAll('.note-card');
                    let found = false;
                    for (let i = 0; i < notes.length; i++) {
                        const button = notes[i].querySelector(`.delete-btn[onclick*="${noteId}"]`);
                        if (button) {
                            notes[i].remove();
                            found = true;
                            showMessage('success', 'Note deleted successfully');
                            break;
                        }
                    }
                    if (!found) {
                        console.error('Could not find note element to remove');
                        showMessage('error', 'Could not find note element to remove');
                        window.location.reload();
                    }
                }
            } else {
                console.error('Delete failed:', data.error || 'Unknown error');
                showMessage('error', `Delete failed: ${data.error || 'Unknown error'}`);
            }
        })
        .catch(error => {
            console.error('Delete error:', error);
            showMessage('error', `Error deleting note: ${error.message}`);
        });
    }
}

function cleanupApp() {
    console.log('Cleaning up notes app');
}

window.initializeApp = initializeApp;
window.cleanupApp = cleanupApp;

console.log('Notes script loaded and functions defined');
