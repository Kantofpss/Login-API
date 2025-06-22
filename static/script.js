document.getElementById('load-users').addEventListener('click', async () => {
    try {
        const response = await fetch('/admin/api/users', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ password: 'admin123' }) // Aqui a senha deve ser enviada
        });

        if (!response.ok) {
            throw new Error('Falha na autenticação ou erro no servidor.');
        }

        const users = await response.json();
        const tableBody = document.getElementById('user-table-body');
        tableBody.innerHTML = ''; // Limpa a tabela
        users.forEach(user => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${user.username}</td>
                <td>${user.hwid || 'Nenhum'}</td>
                <td><button onclick="resetHwid('${user.username}')">Resetar HWID</button></td>
            `;
            tableBody.appendChild(row);
        });
    } catch (error) {
        alert(`Erro ao carregar usuários: ${error.message}`);
    }
});