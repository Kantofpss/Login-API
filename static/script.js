document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('load-users').addEventListener('click', async () => {
        try {
            const response = await fetch('/admin/api/users', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: 'admin123' })
            });

            if (!response.ok) {
                throw new Error('Falha na autenticação ou erro no servidor: ' + response.status);
            }

            const users = await response.json();
            const tableBody = document.getElementById('user-table-body');
            tableBody.innerHTML = '';
            users.forEach(user => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${user.username}</td>
                    <td>${user.hwid || 'Nenhum'}</td>
                    <td>
                        <button onclick="resetHwid('${user.username}')">Resetar HWID</button>
                        <button onclick="deleteUser('${user.username}')">Deletar</button>
                    </td>
                `;
                tableBody.appendChild(row);
            });
        } catch (error) {
            alert(`Erro ao carregar usuários: ${error.message}`);
        }
    });

    window.createUser = function() {
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        fetch('/admin/api/create_user', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password: 'admin123', username, password_user: password })
        }).then(response => response.json())
          .then(data => alert(data.success || data.error))
          .catch(error => alert('Erro ao criar usuário: ' + error));
    };

    window.resetHwid = function(username) {
        fetch('/admin/api/reset_hwid', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password: 'admin123', username })
        }).then(response => response.json())
          .then(data => alert(data.success || data.error))
          .catch(error => alert('Erro ao resetar HWID: ' + error));
    };

    window.deleteUser = function(username) {
        if (confirm(`Tem certeza que deseja deletar o usuário ${username}?`)) {
            fetch('/admin/api/delete_user', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: 'admin123', username })
            }).then(response => response.json())
              .then(data => alert(data.success || data.error))
              .catch(error => alert('Erro ao deletar usuário: ' + error));
        }
    };
});