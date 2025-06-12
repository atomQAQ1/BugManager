// 通用工具函数
function showAlert(message, type = 'success') {
    const alertBox = document.createElement('div');
    alertBox.className = `alert ${type}`;
    alertBox.textContent = message;
    document.body.appendChild(alertBox);
    setTimeout(() => alertBox.remove(), 3000);
}

//模态框控制函数
function showModal(message, type = 'success') {
    const modal = document.getElementById('resultModal');
    const modalMessage = document.getElementById('modalMessage');

    modalMessage.textContent = message;
    modal.style.display = 'block';
}

function closeModal() {
    const modal = document.getElementById('resultModal');
    modal.style.display = 'none';
}

export { showAlert, showModal, closeModal };
window.closeModal=closeModal;