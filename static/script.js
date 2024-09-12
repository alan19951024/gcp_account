document.getElementById('file1Button').addEventListener('click', function() {
    document.getElementById('file1').click();
});

document.getElementById('file1').addEventListener('change', function() {
    document.getElementById('file1Name').textContent = this.files[0].name;
});

document.getElementById('file2Button').addEventListener('click', function() {
    document.getElementById('file2').click();
});

document.getElementById('file2').addEventListener('change', function() {
    document.getElementById('file2Name').textContent = this.files[0].name;
});

document.getElementById('templateButton').addEventListener('click', function() {
    document.getElementById('template').click();
});

document.getElementById('template').addEventListener('change', function() {
    document.getElementById('templateName').textContent = this.files[0].name;
});

document.getElementById('clearButton').addEventListener('click', function() {
    document.getElementById('file1').value = '';
    document.getElementById('file1Name').textContent = '';
    document.getElementById('file2').value = '';
    document.getElementById('file2Name').textContent = '';
    document.getElementById('template').value = '';
    document.getElementById('templateName').textContent = '';
    
    // 清除處理好的檔案並還原按鈕樣式
    const downloadButton = document.getElementById('downloadButton');
    downloadButton.disabled = true;
    downloadButton.classList.remove('completed');
    downloadButton.onclick = null;
});

document.getElementById('uploadForm').addEventListener('submit', function(event) {
    event.preventDefault();
    document.getElementById('loading').style.display = 'block';
    const formData = new FormData(this);
    fetch('https://gcp-account.onrender.com/upload', { // 確保 URL 正確
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        document.getElementById('loading').style.display = 'none';
        if (data.success) {
            const downloadButton = document.getElementById('downloadButton');
            downloadButton.disabled = false;
            downloadButton.classList.add('completed'); 
            downloadButton.onclick = function() {
                const link = document.createElement('a');
                link.href = `https://gcp-account.onrender.com/download/${data.filename}`;
                link.download = data.filename;
                link.click()
            };
        } else {
            alert('檔案處理失敗: ' + data.message);
        }
    })
    .catch(error => {
        document.getElementById('loading').style.display = 'none';
        console.error('Error:', error);
        alert('檔案處理失敗: ' + error.message);
    });
});

