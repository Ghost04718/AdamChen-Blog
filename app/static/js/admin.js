// 添加 CSRF token 到所有 AJAX 请求
function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').content;
}

// 删除评论
function deleteComment(commentId) {
    if (confirm('确定要删除这条评论吗？')) {
        fetch(`/admin/comment/${commentId}/delete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            if (data.success) {
                document.querySelector(`.comment-item[data-id="${commentId}"]`).remove();
            } else {
                alert('删除失败：' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('删除失败，请重试');
        });
    }
}

// 编辑评论
function editComment(commentId) {
    const commentItem = document.querySelector(`.comment-item[data-id="${commentId}"]`);
    const content = commentItem.querySelector('.comment-content').textContent;
    const newContent = prompt('编辑评论内容：', content);
    
    if (newContent && newContent !== content) {
        fetch(`/admin/comment/${commentId}/edit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            credentials: 'same-origin',
            body: JSON.stringify({ content: newContent })
        })
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            if (data.success) {
                commentItem.querySelector('.comment-content').textContent = newContent;
            } else {
                alert('编辑失败：' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('编辑失败，请重试');
        });
    }
} 