document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM Content Loaded - Kaira AI Initializing...');

    // --- CONFIGURATION ---
    // Set this to your Render backend URL (e.g., 'https://kaira-backend.onrender.com') when deploying to Vercel.
    // Keep it as an empty string '' for local development.
    const API_URL = '';

    // --- CHATBOT LOGIC ---
    const chatToggle = document.getElementById('chatToggle');
    const chatWindow = document.getElementById('chatWindow');
    const closeChat = document.getElementById('closeChat');
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    const chatMessages = document.getElementById('chatMessages');
    const iconOpen = document.getElementById('chatIconOpen');
    const iconClose = document.getElementById('chatIconClose');

    if (chatToggle && chatWindow && chatForm) {
        console.log('Chatbot elements found. Initializing toggle logic.');

        // Toggle Chat Window
        const toggleChatWindow = () => {
            console.log('Toggle Chat Window called');
            const isHidden = chatWindow.classList.contains('hidden');
            if (isHidden) {
                // Open
                chatWindow.classList.remove('hidden');
                // Ensure display is block/flex before starting opacity/scale transition
                setTimeout(() => {
                    chatWindow.classList.remove('scale-95', 'opacity-0');
                    chatWindow.classList.add('scale-100', 'opacity-100');
                    if (iconOpen) iconOpen.classList.add('hidden');
                    if (iconClose) iconClose.classList.remove('hidden');
                }, 10);
            } else {
                // Close
                closeChatWindow();
            }
        };

        const closeChatWindow = () => {
            console.log('Close Chat Window called');
            chatWindow.classList.remove('scale-100', 'opacity-100');
            chatWindow.classList.add('scale-95', 'opacity-0');
            if (iconOpen) iconOpen.classList.remove('hidden');
            if (iconClose) iconClose.classList.add('hidden');
            setTimeout(() => {
                chatWindow.classList.add('hidden');
            }, 300);
        };

        // Use onclick directly to be more robust
        chatToggle.onclick = (e) => {
            e.stopPropagation();
            toggleChatWindow();
        };

        if (closeChat) {
            closeChat.onclick = (e) => {
                e.stopPropagation();
                closeChatWindow();
            };
        }

        // Handle Chat Submission
        chatForm.onsubmit = async (e) => {
            e.preventDefault();
            const message = chatInput.value.trim();
            if (!message) return;

            chatInput.value = '';
            addMessageToChat('You', message, 'user');

            const loadingId = 'loading-' + Date.now();
            addLoadingMessage(loadingId);

            try {
                const response = await fetch(`${API_URL}/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });

                if (!response.ok) throw new Error('AI failed to respond');

                const data = await response.json();
                const loaderEl = document.getElementById(loadingId);
                if (loaderEl) loaderEl.remove();

                addMessageToChat('Kaira AI', data.response, 'bot');

            } catch (error) {
                console.error('Chat Error:', error);
                const loaderEl = document.getElementById(loadingId);
                if (loaderEl) loaderEl.remove();
                addMessageToChat('System', 'Sorry, I couldn\'t connect to the AI brain. Please try again later.', 'error');
            }
        };

        function addMessageToChat(sender, text, type) {
            const msgDiv = document.createElement('div');
            msgDiv.className = `flex flex-col gap-1 ${type === 'user' ? 'items-end' : 'items-start'} max-w-[85%] ${type === 'user' ? 'ml-auto' : ''}`;

            const senderSpan = document.createElement('span');
            senderSpan.className = `text-[10px] font-bold uppercase ${type === 'user' ? 'text-slate-500 mr-1' : 'text-primary ml-1'}`;
            senderSpan.textContent = sender;

            const textDiv = document.createElement('div');
            let bubbleClasses = 'p-3 text-xs leading-relaxed rounded-2xl';
            if (type === 'user') {
                bubbleClasses += ' bg-white/10 text-slate-100 rounded-tr-none';
            } else if (type === 'bot') {
                bubbleClasses += ' bg-primary/10 border border-primary/20 text-slate-100 rounded-tl-none';
            } else {
                bubbleClasses += ' bg-red-500/10 border border-red-500/20 text-red-400 rounded-tl-none';
            }
            textDiv.className = bubbleClasses;
            textDiv.textContent = text;

            msgDiv.appendChild(senderSpan);
            msgDiv.appendChild(textDiv);
            chatMessages.appendChild(msgDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function addLoadingMessage(id) {
            const msgDiv = document.createElement('div');
            msgDiv.id = id;
            msgDiv.className = 'flex flex-col gap-1 items-start max-w-[85%]';
            msgDiv.innerHTML = `
                <span class="text-[10px] text-primary font-bold uppercase ml-1">Kaira AI</span>
                <div class="bg-primary/10 border border-primary/20 rounded-2xl rounded-tl-none p-3 text-xs text-slate-100 flex items-center gap-2">
                    Thinking... <div class="size-2 bg-primary rounded-full animate-pulse"></div>
                </div>
            `;
            chatMessages.appendChild(msgDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }


    // --- AUTH GUARD ---
    const token = localStorage.getItem('token');
    const path = window.location.pathname;
    const isAuthPage = path.includes('login.html') || path.includes('signup.html') || path.includes('home.html') || path === '/' || path.endsWith('/frontend/');
    // basic check, might need adjustment based on how it's served. 
    // If serving via FastAPI static files, path might be /app/index.html etc.

    // Simple logic: If we are on index.html (the tool) and no token, redirect to login
    if (!token && (path.includes('index.html') || path.endsWith('/app/'))) {
        window.location.href = 'login.html';
    }

    // If on login/signup and have token, redirect to app
    if (token && (path.includes('login.html') || path.includes('signup.html'))) {
        window.location.href = 'index.html';
    }

    // --- FETCH USER PROFILE ---
    if (token) {
        fetchUser(token);
    }

    async function fetchUser(token) {
        try {
            const response = await fetch(`${API_URL}/users/me`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                if (response.status === 401) {
                    localStorage.removeItem('token');
                    // Optional: Redirect to login or just refresh to clear state
                    // window.location.href = 'login.html';
                }
                return;
            }

            const user = await response.json();
            updateAuthUI(user);

        } catch (error) {
            console.error('Failed to fetch user:', error);
        }
    }

    function updateAuthUI(user) {
        const authLinks = document.getElementById('authLinks');
        const userProfile = document.getElementById('userProfile');
        const userName = document.getElementById('userName');
        const userAvatar = document.getElementById('userAvatar');

        if (user && userProfile) {
            if (authLinks) authLinks.classList.add('hidden'); // Use class hidden for Tailwind consistency
            if (authLinks) authLinks.style.display = 'none'; // Double down to be safe

            userProfile.classList.remove('hidden');
            userProfile.style.display = 'flex';

            if (user.role === 'admin' && !document.getElementById('adminDashLink')) {
                const dashLink = document.createElement('a');
                dashLink.id = 'adminDashLink';
                dashLink.href = 'admin.html';
                dashLink.className = 'px-3 py-1 bg-primary/10 text-primary border border-primary/20 rounded-lg text-xs font-bold uppercase tracking-wider hover:bg-primary hover:text-black transition-colors';
                dashLink.textContent = 'Dashboard';
                // Insert before username
                userProfile.insertBefore(dashLink, userName);
            }

            if (userName) userName.textContent = user.name;
            if (userAvatar) {
                userAvatar.src = user.profile_image || `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name)}&background=random`;
            }

            // Admin Sidebar
            const adminName = document.getElementById('adminNameDisplay');
            const adminAvatar = document.getElementById('adminAvatarLetters');
            if (adminName) adminName.textContent = user.name;
            if (adminAvatar) {
                const initials = user.name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
                adminAvatar.textContent = initials;
            }
        }
    }

    // --- LOGOUT LOGIC ---
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.removeItem('token');
            window.location.href = 'home.html'; // or login.html
        });
    }

    // --- LOGIN LOGIC ---
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;
            const btn = document.getElementById('loginBtn');
            const loader = document.getElementById('loginLoader');

            btn.disabled = true;
            loader.style.display = 'inline-block';

            try {
                const response = await fetch(`${API_URL}/users/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email, password }),
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.detail || 'Login failed');
                }

                localStorage.setItem('token', data.access_token);

                // Fetch user to check role for redirect
                try {
                    const userResponse = await fetch(`${API_URL}/users/me`, {
                        headers: { 'Authorization': `Bearer ${data.access_token}` }
                    });
                    if (userResponse.ok) {
                        const user = await userResponse.json();
                        if (user.role === 'admin') {
                            window.location.href = 'admin.html';
                        } else {
                            window.location.href = 'index.html';
                        }
                    } else {
                        window.location.href = 'index.html';
                    }
                } catch (e) {
                    window.location.href = 'index.html';
                }

            } catch (error) {
                alert(error.message);
            } finally {
                btn.disabled = false;
                loader.style.display = 'none';
            }
        });
    }

    // --- SIGNUP LOGIC ---
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            const profileImage = document.getElementById('profileImage').files[0];
            const btn = document.getElementById('signupBtn');
            const loader = document.getElementById('signupLoader');

            if (password !== confirmPassword) {
                alert("Passwords do not match!");
                return;
            }

            btn.disabled = true;
            loader.style.display = 'inline-block';

            const formData = new FormData();
            formData.append('name', name);
            formData.append('email', email);
            formData.append('password', password);
            formData.append('confirm_password', confirmPassword);
            if (profileImage) {
                formData.append('profile_image', profileImage);
            }

            try {
                const response = await fetch(`${API_URL}/users/register`, {
                    method: 'POST',
                    body: formData // No Content-Type header when sending FormData
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.detail || 'Registration failed');
                }

                alert('Registration successful! Please login.');
                window.location.href = 'login.html';

            } catch (error) {
                alert(error.message);
            } finally {
                btn.disabled = false;
                loader.style.display = 'none';
            }
        });
    }


    // --- EXISTING APP LOGIC (Run only if elements exist) ---
    const uploadArea = document.getElementById('uploadArea');
    if (uploadArea) {
        const fileInput = document.getElementById('fileInput');
        const previewContainer = document.getElementById('previewContainer');
        const imagePreview = document.getElementById('imagePreview');
        const analyzeBtn = document.getElementById('analyzeBtn');
        const loader = document.getElementById('loader');
        const resultsSection = document.getElementById('resultsSection');

        let currentFile = null;

        // --- Drag & Drop Handlers ---
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, unhighlight, false);
        });

        function highlight() {
            uploadArea.classList.add('dragover');
        }

        function unhighlight() {
            uploadArea.classList.remove('dragover');
        }

        uploadArea.addEventListener('drop', handleDrop, false);

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            handleFiles(files);
        }

        // --- Click Handler ---
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });

        fileInput.addEventListener('change', function () {
            handleFiles(this.files);
        });

        function handleFiles(files) {
            if (files.length > 0) {
                currentFile = files[0];
                previewFile(currentFile);
            }
        }

        function previewFile(file) {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onloadend = function () {
                imagePreview.src = reader.result;
                previewContainer.style.display = 'block';
                resultsSection.style.display = 'none'; // Hide previous results
                // Scroll to preview
                previewContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        }

        // --- Analysis Handler ---
        analyzeBtn.addEventListener('click', async () => {
            const speciesInput = document.getElementById('speciesInput');
            const textValue = speciesInput.value.trim();

            if (!currentFile && !textValue) {
                alert("Please upload an image or enter a species name.");
                return;
            }

            // UI Loading State
            analyzeBtn.disabled = true;
            analyzeBtn.innerHTML = 'Analyzing with Kaira AI... <div class="loader" style="display:inline-block"></div>';

            const formData = new FormData();

            if (currentFile) {
                formData.append('file', currentFile);
            }

            if (textValue) {
                formData.append('text', textValue);
            }

            try {
                // Updated to point to the Kaira AI endpoint
                const response = await fetch(`${API_URL}/identify`, {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error(`Server error: ${response.statusText}`);
                }

                const data = await response.json();
                displayResults(data);

            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred during analysis. Please try again.');
            } finally {
                analyzeBtn.disabled = false;
                analyzeBtn.textContent = 'Analyze Species';
            }
        });

        function displayResults(data) {
            // Populate Data
            document.getElementById('resSpecies').textContent = data.species;
            document.getElementById('resConfidence').textContent = `${(data.confidence * 100).toFixed(1)}% Match`;

            const details = data.details || {};
            document.getElementById('resSubtitle').textContent = details.scientific_name || 'Scientific Name Unknown';
            document.getElementById('resHabitat').textContent = details.habitat || 'N/A';
            document.getElementById('resDistribution').textContent = details.distribution || 'N/A';
            document.getElementById('resStatus').textContent = details.conservation_status || 'N/A';
            document.getElementById('resRole').textContent = details.ecological_importance || 'N/A';
            document.getElementById('resDescription').textContent = details.description || 'No detailed description available for this species.';

            // Show Section
            resultsSection.style.display = 'grid';
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
});

// --- ADMIN DASHBOARD LOGIC (Global Scope) ---

async function initAdminDashboard() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    // Setup Admin Details in Sidebar
    const adminLogoutBtn = document.getElementById('adminLogoutBtn');
    if (adminLogoutBtn) {
        adminLogoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.removeItem('token');
            window.location.href = 'login.html';
        });
    }

    fetchAdminData();
    fetchSystemStats(token);
}

async function fetchAdminData() {
    const token = localStorage.getItem('token');
    const tableBody = document.getElementById('usersTableBody');
    const totalUsersEl = document.getElementById('statTotalUsers');

    try {
        const response = await fetch(`${API_URL}/admin/users`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.status === 403) {
            alert("Access Denied: Admin privileges required.");
            // Redirect to home if not admin
            window.location.href = 'index.html';
            return;
        }

        if (!response.ok) throw new Error("Failed to load admin data");

        const users = await response.json();

        // Update Stats
        if (totalUsersEl) totalUsersEl.textContent = users.length;

        // Render Table
        if (tableBody) {
            tableBody.innerHTML = '';
            users.forEach(user => {
                const tr = document.createElement('tr');
                tr.className = 'table-row-hover group border-b border-white/5 last:border-0';

                // Handle Avatar
                let avatarSrc = user.profile_image || `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name)}&background=random`;

                // Mask email if admin
                const displayEmail = user.role === 'admin' ? user.email.replace(/(.).*@/, 'admin@****') : user.email;

                tr.innerHTML = `
                    <td class="px-6 py-4">
                        <div class="flex items-center gap-3">
                            <img src="${avatarSrc}" class="w-8 h-8 rounded-full border border-white/10 object-cover">
                            <span class="font-bold text-white">${user.name}</span>
                        </div>
                    </td>
                    <td class="px-6 py-4">
                        <span class="px-2 py-1 rounded-md text-xs font-bold uppercase tracking-wider ${user.role === 'admin' ? 'bg-primary/20 text-primary' : 'bg-white/10 text-slate-400'}">
                            ${user.role || 'User'}
                        </span>
                    </td>
                    <td class="px-6 py-4 text-slate-400">${displayEmail}</td>
                    <td class="px-6 py-4 text-right">
                        <button onclick="deleteUser('${user.id}')" class="text-slate-500 hover:text-red-500 transition-colors p-2 hover:bg-red-500/10 rounded-lg" title="Delete User">
                            <span class="material-symbols-outlined text-lg">delete</span>
                        </button>
                    </td>
                `;
                tableBody.appendChild(tr);
            });
        }

    } catch (error) {
        console.error(error);
        if (tableBody) tableBody.innerHTML = '<tr><td colspan="4" class="text-center py-8 text-red-400">Error loading data. Ensure you are an Admin.</td></tr>';
    }
}

async function deleteUser(userId) {
    if (!confirm("Are you sure you want to delete this user? This action cannot be undone.")) return;

    const token = localStorage.getItem('token');
    try {
        const response = await fetch(`${API_URL}/admin/users/${userId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            fetchAdminData(); // Refresh list
        } else {
            const data = await response.json();
            alert(data.detail || "Failed to delete user");
        }
    } catch (error) {
        console.error(error);
        alert("An error occurred");
    }
}

async function fetchSystemStats(token) {
    try {
        const response = await fetch(`${API_URL}/admin/stats`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            const stats = await response.json();
            // Update UI elements if they exist
            const logsEl = document.getElementById('statSpeciesLogs'); // Need to ensure this ID exists in HTML
            const serverEl = document.getElementById('statServerStatus');

            if (logsEl) logsEl.textContent = stats.species_logs;
            if (serverEl) serverEl.textContent = stats.server_status;
        }
    } catch (e) {
        console.error("Failed to fetch stats", e);
    }
}

// Expose functions to window for HTML access
window.initAdminDashboard = initAdminDashboard;
window.fetchAdminData = fetchAdminData;
window.deleteUser = deleteUser;

