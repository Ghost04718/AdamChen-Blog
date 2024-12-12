document.addEventListener('DOMContentLoaded', function() {
    console.log('Post script loaded');
    const likeBtns = document.querySelectorAll('.like-btn');
    console.log('Like buttons:', likeBtns);
    
    likeBtns.forEach(btn => {
        // 初始化按钮状态
        if (btn.dataset.liked === 'true') {
            btn.classList.add('liked');
        }
        
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();  // 阻止事件冒泡
            
            console.log('Like button clicked');
            const isLiked = this.dataset.liked === 'true';
            console.log('Is liked:', isLiked);
            
            if (isLiked) {
                console.log('Already liked');
                return;
            }

            const postId = this.dataset.postId;
            console.log('Post ID:', postId);
            const csrf_token = document.querySelector('meta[name="csrf-token"]').content;
            
            // 禁用按钮防止重复点击
            this.disabled = true;
            
            fetch(`/post/${postId}/like`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrf_token
                },
                body: JSON.stringify({ post_id: postId }),
                credentials: 'same-origin'
            })
            .then(response => {
                console.log('Response status:', response.status);
                if (!response.ok) {
                    throw new Error('点赞失败');
                }
                return response.json();
            })
            .then(data => {
                console.log('Response data:', data);
                if (data.error) {
                    throw new Error(data.error);
                }
                if (data.likes !== undefined) {
                    this.querySelector('.like-count').textContent = data.likes;
                    this.classList.add('liked');
                    this.dataset.liked = 'true';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert(error.message || '点赞失败，请重试');
            })
            .finally(() => {
                // 恢复按钮状态
                this.disabled = false;
            });
        });
    });
}); 