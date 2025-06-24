document.addEventListener('DOMContentLoaded', () => {
    const loginSection = document.getElementById('admin-login');
    const adminPanel = document.getElementById('admin-panel');
    const loginForm = document.getElementById('login-form');
    const logoutButton = document.getElementById('logout-button');
    const userList = document.getElementById('user-list');
    const loginError = document.getElementById('login-error');

    // NOVO: Elementos do formulário de adicionar usuário
    const addUserForm = document.getElementById('add-user-form');
    const newNameInput = document.getElementById('new-name');
    const newEmailInput = document.getElementById('new-email');
    const newPasswordInput = document.getElementById('new-password');
    const addUserMessage = document.getElementById('add-user-message');

    const API_URL = 'https://marin-login-api.onrender.com'; // Sua URL base da API no Render

    // Função para obter o token do localStorage
    const getToken = () => localStorage.getItem('access_token');

    // Função para fazer login
    const login = async (event) => {
        event.preventDefault();
        loginError.textContent = '';
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        try {
            const response = await fetch(`${API_URL}/admin/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('access_token', data.access_token);
                showAdminPanel();
            } else {
                loginError.textContent = 'Credenciais inválidas.';
            }
        } catch (error) {
            console.error('Erro de login:', error);
            loginError.textContent = 'Erro ao tentar conectar com o servidor.';
        }
    };

    // Função para buscar e exibir os usuários
    const fetchUsers = async () => {
        const token = getToken();
        if (!token) return;

        try {
            const response = await fetch(`${API_URL}/users`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            
            if (response.status === 401 || response.status === 403) {
                 logout(); // Token inválido ou expirado
                 return;
            }

            const users = await response.json();
            userList.innerHTML = ''; // Limpa a lista antes de preencher

            users.forEach(user => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${user.id}</td>
                    <td>${user.name}</td>
                    <td>${user.email}</td>
                    <td><button onclick="deleteUser(${user.id})">Excluir</button></td>
                `;
                userList.appendChild(tr);
            });
        } catch (error) {
            console.error('Erro ao buscar usuários:', error);
        }
    };

    // Função para deletar um usuário
    window.deleteUser = async (userId) => {
        if (!confirm(`Tem certeza que deseja excluir o usuário com ID ${userId}?`)) return;

        const token = getToken();
        try {
            const response = await fetch(`${API_URL}/admin/users/${userId}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });

            const data = await response.json();
            alert(data.message); // Exibe a mensagem de sucesso ou erro

            if (response.ok) {
                fetchUsers(); // Atualiza a lista de usuários após a exclusão
            }
        } catch (error) {
            console.error('Erro ao excluir usuário:', error);
            alert('Erro ao conectar com o servidor.');
        }
    };

    // NOVO: Função para adicionar um novo usuário
    const addUser = async (event) => {
        event.preventDefault();
        addUserMessage.textContent = '';
        const token = getToken();

        const newUser = {
            name: newNameInput.value,
            email: newEmailInput.value,
            password: newPasswordInput.value
        };

        try {
            const response = await fetch(`${API_URL}/admin/users`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(newUser)
            });

            const data = await response.json();
            addUserMessage.textContent = data.message;

            if (response.ok) {
                addUserMessage.style.color = 'green';
                fetchUsers(); // Atualiza a lista para mostrar o novo usuário
                addUserForm.reset(); // Limpa o formulário
            } else {
                 addUserMessage.style.color = 'red';
            }
        } catch (error) {
            console.error('Erro ao adicionar usuário:', error);
            addUserMessage.textContent = 'Erro ao conectar com o servidor.';
            addUserMessage.style.color = 'red';
        }
    };

    // Função para fazer logout
    const logout = () => {
        localStorage.removeItem('access_token');
        loginSection.classList.remove('hidden');
        adminPanel.classList.add('hidden');
    };

    // Função para mostrar o painel principal
    const showAdminPanel = () => {
        loginSection.classList.add('hidden');
        adminPanel.classList.remove('hidden');
        fetchUsers();
    };

    // Event Listeners
    loginForm.addEventListener('submit', login);
    logoutButton.addEventListener('click', logout);
    addUserForm.addEventListener('submit', addUser); // NOVO

    // Verifica se já existe um token ao carregar a página
    if (getToken()) {
        showAdminPanel();
    }
});