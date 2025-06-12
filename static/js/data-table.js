import { showAlert, showModal } from './utils.js';
let currentEditId = null;
// 删除记录功能
async function deleteRecord(id) {
    if (!confirm(`确定要删除该记录吗？`)) return;
    
    try {
        const response = await fetch(`/delete_record/${id}`, {
            method: 'DELETE'
        });
        const data = await response.json();
        if (data.success) {
            showAlert('记录删除成功');
            setTimeout(() => location.reload(), 1000);
        } else {
            showAlert(data.error || '删除失败', 'error');
        }
    } catch (error) {
        showAlert('请求失败: ' + error.message, 'error');
    }
}

// 全选/取消全选
// 在文件顶部添加常量
const SELECTED_IDS_KEY = 'selected_ids';
const ALL_RECORD_IDS_KEY = 'all_record_ids'; 

const SELECT_ALL_MODE = {
    PAGE: 'page',
    ALL: 'all'
};

// 修改toggleSelectAll函数
// 在文件顶部常量定义之后添加
function updateSelectAllCheckbox() {
    const checkboxes = document.querySelectorAll('.record-checkbox');
    const selectAll = document.getElementById('select-all');
    if (checkboxes.length > 0) {
        const allChecked = Array.from(checkboxes).every(cb => cb.checked);
        selectAll.checked = allChecked;
    }
}

// 在toggleSelectAll函数中修改，确保调用updateSelectAllCheckbox
function toggleSelectAll(checkbox) {
    const mode = document.getElementById('select-all-mode').value;
    if (mode === SELECT_ALL_MODE.PAGE) {
        // 选择当前页数据
        const checkboxes = document.querySelectorAll('.record-checkbox');
        checkboxes.forEach(cb => {
            cb.checked = checkbox.checked;
        });
    } else {
        // 选择全部数据
        if (checkbox.checked) {
            selectAllRecords();
        } else {
            clearAllSelections();
        }
    }
    updateSelectAllCheckbox();  
}

// 添加新函数 - 选择全部数据
async function selectAllRecords() {
    try {
        const response = await fetch('/get_all_record_ids', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                // 传递当前筛选条件
                search_params: getCurrentSearchParams()
            })
        });
        const data = await response.json();
        
        if (data.success && data.ids) {
            // 存储所有ID到sessionStorage
            sessionStorage.setItem(ALL_RECORD_IDS_KEY, JSON.stringify(data.ids));
            // 勾选当前页中存在的记录
            const checkboxes = document.querySelectorAll('.record-checkbox');
            checkboxes.forEach(cb => {
                if (data.ids.includes(cb.value)) {
                    cb.checked = true;
                }
            });
            updateSelectAllCheckbox();
        }
    } catch (error) {
        showAlert('获取全部记录ID失败: ' + error.message, 'error');
    }
}

// 添加新函数 - 清除所有选择
function clearAllSelections() {
    const checkboxes = document.querySelectorAll('.record-checkbox');
    checkboxes.forEach(cb => {
        cb.checked = false;
    });
    sessionStorage.removeItem(ALL_RECORD_IDS_KEY);
}
//获取当前筛选条件
function getCurrentSearchParams() {
    const urlParams = new URLSearchParams(window.location.search);
    const searchParams = [];
    
    // 使用 Map 存储参数索引避免重复
    const paramIndices = new Set();
    
    urlParams.forEach((value, key) => {
        if (key.startsWith('search_column_')) {
            const index = key.split('_').pop();
            paramIndices.add(index);
        }
    });

    // 为每个找到的索引构建搜索参数
    paramIndices.forEach(index => {
        const column = urlParams.get(`search_column_${index}`);
        const value = urlParams.get(`search_value_${index}`);
        if (column && value) {
            searchParams.push({
                column: column,
                value: value
            });
        }
    });
    
    return searchParams;
}
// 添加新函数 - 切换选择模式
function changeSelectAllMode(select) {
    if (select.value === SELECT_ALL_MODE.ALL) {
        // 切换到"选择全部"模式时自动选中当前页所有记录
        document.getElementById('select-all').checked = true;
        toggleSelectAll(document.getElementById('select-all'));
    }
}

// 在window导出中添加新函数
window.changeSelectAllMode = changeSelectAllMode;

// 批量操作
async function applyBatchAction() {
    const action = document.getElementById('batch-action').value;
    if (!action) {
        showAlert('请选择操作类型', 'error');
        return;
    }

    const mode = document.getElementById('select-all-mode').value;
    let ids = [];
    
    if (mode === SELECT_ALL_MODE.ALL) {
        // 如果是全选模式，从sessionStorage获取所有ID
        const allIds = JSON.parse(sessionStorage.getItem(ALL_RECORD_IDS_KEY) || '[]');
        ids = allIds;
    } else {
        // 否则获取当前页选中的ID
        const checkedBoxes = document.querySelectorAll('.record-checkbox:checked');
        if (checkedBoxes.length === 0) {
            showAlert('请至少选择一条记录', 'error');
            return;
        }
        ids = Array.from(checkedBoxes).map(box => box.value);
    }
    
    if (action === 'delete' && !confirm(`确定要删除选中的 ${ids.length} 条记录吗？`)) {
        return;
    }
    if (action === 'remind' &&!confirm(`确定要提醒选中 ${ids.length}条目对应的安全员吗？`)) {
        return;
    }
    if (action === 'modify'){
        showModifyModal(); // 添加这行触发模态框
        sessionStorage.setItem('current_batch_ids', JSON.stringify(ids));
        return; // 添加这行终止后续操作
    }

    try {
        const response = await fetch('/batch_operation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                action: action,
                ids: ids
            })
        });
        const data = await response.json();
        if (data.success) {
            document.querySelectorAll('.record-checkbox:checked').forEach(checkbox => {
                checkbox.checked = false;
            });
            document.getElementById('select-all').checked = false;
            sessionStorage.removeItem(SELECTED_IDS_KEY);
            sessionStorage.removeItem(ALL_RECORD_IDS_KEY);
            updateSelectAllCheckbox();
            const actionNames = {
                'delete': '删除',
                'export': '导出',
                'remind': '提醒'
            };
            showAlert(`批量${actionNames[action]}操作成功`);
            // 添加提醒后的页面刷新
            if (action === 'delete' || action === 'remind') {
                setTimeout(() => location.reload(), 1000);
            }
        } else {
            showAlert(data.error || '操作失败', 'error');
        }
    } catch (error) {
        showAlert('请求失败: ' + error.message, 'error');
    }
}

// 搜索功能
function addSearchGroup() {
    const container = document.querySelector('.search-container');
    const firstGroup = document.querySelector('.search-group');
    
    const newGroup = firstGroup.cloneNode(true);
    newGroup.querySelector('.search-value').value = '';
    
    const addButton = container.querySelector('button[onclick="addSearchGroup()"]');
    container.insertBefore(newGroup, addButton);
}

function removeSearchGroup(button) {
    const group = button.parentElement;
    if (document.querySelectorAll('.search-group').length > 1) {
        group.remove();
    } else {
        group.querySelector('.search-column').selectedIndex = 0;
        group.querySelector('.search-value').value = '';
    }
}

// 应用筛选
function applySearch() {
    const searchGroups = document.querySelectorAll('.search-group');
    const searchParams = [];
    
    searchGroups.forEach(group => {
        const column = group.querySelector('.search-column').value;
        const value = group.querySelector('.search-value').value.trim();
        
        if (value) {
            searchParams.push({
                column: column,
                value: value
            });
        }
    });
    
    if (searchParams.length === 0) {
        showAlert('请输入至少一个筛选条件', 'error');
        return;
    }
    
    const url = new URL(window.location.href);
    url.searchParams.delete('search_column');
    url.searchParams.delete('search_value');
    
    searchParams.forEach((param, index) => {
        url.searchParams.set(`search_column_${index}`, param.column);
        url.searchParams.set(`search_value_${index}`, param.value);
    });
    
    url.searchParams.set('page', 1);
    window.location.href = url.toString();
}

// 重置筛选
function resetSearch() {
    const url = new URL(window.location.href);
    // 移除所有搜索参数
    [...url.searchParams.keys()].forEach(key => {
        if (key.startsWith('search_column_') || key.startsWith('search_value_')) {
            url.searchParams.delete(key);
        }
    });
    url.searchParams.set('page', 1);
    window.location.href = url.toString();
}
function editRecord(recordId) {
    currentEditId = recordId;
    const row = document.querySelector(`tr input[value="${recordId}"]`).closest('tr');
    const cells = row.querySelectorAll('td[data-content]');
    
    const fieldsContainer = document.getElementById('editFields');
    fieldsContainer.innerHTML = '';
    //获取列名：
    const headers = document.querySelectorAll('thead th[data-content]');
    cells.forEach((cell, index) => {
        const columnName = headers[index].getAttribute('data-content');
        const value = cell.textContent.trim();
        
        fieldsContainer.innerHTML += `
            <div class="form-group">
                <label>${columnName}:</label>
                <input type="text" class="edit-input" 
                       name="${columnName}" 
                       value="${value}"
                       data-column="${columnName}">
            </div>
        `;
    });
    
    document.getElementById('editModal').style.display = 'block';
}

function submitEdit(e) {
    e.preventDefault();
    const formData = {};
    document.querySelectorAll('.edit-input').forEach(input => {
        formData[input.dataset.column] = input.value;
    });

    saveEdit(currentEditId, formData);
}

function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
    currentEditId = null;
}

async function saveEdit(recordId, updates) {
    try {
        console.log('更新数据:', { recordId, updates });
        const response = await fetch(`/update_record/${recordId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(updates)
        });
        
        const result = await response.json();
        if (result.success) {
            showAlert('更新成功');
            setTimeout(() => location.reload(), 1000);
        } else {
            showAlert(result.error || '更新失败', 'error');
        }
    } catch (error) {
        showAlert('请求失败: ' + error.message, 'error');
    } finally {
        closeEditModal();
    }
}
function showModifyModal() {
    document.getElementById('modifyModal').style.display = 'block';
}

function closeModifyModal() {
    document.getElementById('modifyModal').style.display = 'none';
}

async function submitBatchModify(e) {
    e.preventDefault();
    const column = document.getElementById('modifyColumn').value;
    const value = document.getElementById('modifyValue').value;
    const ids = JSON.parse(sessionStorage.getItem('current_batch_ids') || '[]');
    
    // console.log('批量修改:', { column, value });
    try {
        const response = await fetch('/batch_operation', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                action: 'modify',
                ids: ids,
                column: column,
                value: value
            })
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
        }
        const data = await response.json();
        if (data.success) {
            showAlert('批量修改成功');
            setTimeout(() => location.reload(), 1000);
        } else {
            showAlert('修改失败: ' + (data.error || '未知错误'), 'error');
        }
        closeModifyModal();
    } catch (error) {
        showAlert('请求失败: ' + error.message, 'error');
    }
}
async function handleDataUpload(file) {
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/upload_data', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        if (result.success) {
            showAlert('数据上传成功，3秒后刷新页面...');
            setTimeout(() => location.reload(), 3000);
        } else {
            showAlert(`上传失败: ${result.error}`, 'error');
        }
    } catch (error) {
        showAlert(`请求失败: ${error.message}`, 'error');
    }
}

// 在window对象上暴露函数
window.uploadDataFile = () => {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.xlsx,.xls';
    fileInput.onchange = (e) => {
        const file = e.target.files[0];
        if (file) handleDataUpload(file);
    };
    fileInput.click()
};

window.closeModifyModal = closeModifyModal;
window.submitBatchModify = submitBatchModify;
window.editRecord = editRecord;
window.submitEdit = submitEdit;
window.closeEditModal = closeEditModal;
window.deleteRecord = deleteRecord;
window.toggleSelectAll = toggleSelectAll;
window.applyBatchAction = applyBatchAction;
window.addSearchGroup = addSearchGroup;
window.removeSearchGroup = removeSearchGroup;
window.applySearch = applySearch;
window.resetSearch = resetSearch;