document.addEventListener('DOMContentLoaded', function() {
    // 为所有代码块添加复制按钮
    document.querySelectorAll('pre').forEach(function(block) {
        // 创建复制按钮
        const button = document.createElement('button');
        button.className = 'copy-button';
        button.textContent = '复制';
        
        // 创建包装容器
        const wrapper = document.createElement('div');
        wrapper.className = 'code-wrapper';
        
        // 重新组织DOM结构
        block.parentNode.insertBefore(wrapper, block);
        wrapper.appendChild(block);
        wrapper.appendChild(button);
        
        // 添加点击事件
        button.addEventListener('click', function() {
            const code = block.textContent;
            navigator.clipboard.writeText(code).then(function() {
                button.textContent = '已复制!';
                button.classList.add('copied');
                
                setTimeout(function() {
                    button.textContent = '复制';
                    button.classList.remove('copied');
                }, 2000);
            }).catch(function(err) {
                console.error('复制失败:', err);
                button.textContent = '复制失败';
                button.classList.add('error');
                
                setTimeout(function() {
                    button.textContent = '复制';
                    button.classList.remove('error');
                }, 2000);
            });
        });
    });
}); 