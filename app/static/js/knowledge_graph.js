document.addEventListener('DOMContentLoaded', function() {
    // 响应式尺寸设置
    const width = window.innerWidth - 40;
    const height = Math.max(600, window.innerHeight - 200);

    const svg = d3.select('#knowledge-graph')
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .attr('class', 'knowledge-graph-svg');

    // 添加箭头标记定义
    svg.append("defs").append("marker")
        .attr("id", "arrow")
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 20)
        .attr("refY", 0)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M0,-5L10,0L0,5")
        .attr("class", "arrow-head");

    // 创建主容器并添加缩放功能
    const g = svg.append('g');
    const zoom = d3.zoom()
        .scaleExtent([0.2, 3])
        .on('zoom', (event) => {
            g.attr('transform', event.transform);
        });

    svg.call(zoom);

    // 添加图例
    const legend = svg.append("g")
        .attr("class", "legend")
        .attr("transform", "translate(20,20)");

    legend.append("circle")
        .attr("r", 6)
        .style("fill", "#ff6b6b");

    legend.append("text")
        .attr("x", 15)
        .attr("y", 4)
        .text("标签")
        .style("font-size", "12px");

    legend.append("circle")
        .attr("r", 6)
        .attr("cx", 70)
        .style("fill", "#4ecdc4");

    legend.append("text")
        .attr("x", 85)
        .attr("y", 4)
        .text("文章")
        .style("font-size", "12px");

    // 颜色配置
    const color = d3.scaleOrdinal()
        .domain([1, 2])
        .range(['#ff6b6b', '#4ecdc4']);

    // 从API获取数据
    fetch('/api/knowledge-graph')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (!data.nodes || !data.links) {
                throw new Error('Invalid data format');
            }
            const simulation = d3.forceSimulation(data.nodes)
                .force('link', d3.forceLink(data.links)
                    .id(d => d.id)
                    .distance(d => 100 + d.value * 20))
                .force('charge', d3.forceManyBody()
                    .strength(d => d.type === 'tag' ? -200 : -100))
                .force('center', d3.forceCenter(width / 2, height / 2))
                .force('collision', d3.forceCollide().radius(d => Math.sqrt(d.size) * 5 + 10));

            // 创建连接线
            const link = g.append('g')
                .selectAll('line')
                .data(data.links)
                .join('line')
                .attr('class', 'link')
                .style('stroke-width', d => Math.sqrt(d.value))
                .style('stroke', '#999')
                .style('stroke-opacity', 0.6);

            // 创建节点组
            const node = g.append('g')
                .selectAll('g')
                .data(data.nodes)
                .join('g')
                .attr('class', 'node')
                .call(d3.drag()
                    .on('start', dragstarted)
                    .on('drag', dragged)
                    .on('end', dragended));

            // 添加节点圆圈
            node.append('circle')
                .attr('r', d => Math.sqrt(d.size) * 5)
                .style('fill', d => color(d.group))
                .style('stroke', '#fff')
                .style('stroke-width', 2)
                .style('cursor', 'pointer');

            // 添加节点文本
            node.append('text')
                .text(d => d.label)
                .attr('dy', d => Math.sqrt(d.size) * 5 + 15)
                .attr('text-anchor', 'middle')
                .style('font-size', '12px')
                .style('fill', d => document.documentElement.getAttribute('data-theme') === 'dark' ? '#e9ecef' : '#333')
                .style('pointer-events', 'none')
                .style('text-shadow', d => {
                    const theme = document.documentElement.getAttribute('data-theme');
                    return theme === 'dark' 
                        ? '0 1px 3px rgba(0,0,0,0.3)' 
                        : '0 1px 0 #fff, 1px 0 0 #fff, -1px 0 0 #fff, 0 -1px 0 #fff';
                });

            // 添加悬停效果
            node.on('mouseover', function(event, d) {
                d3.select(this).select('circle')
                    .transition()
                    .duration(300)
                    .attr('r', d => Math.sqrt(d.size) * 6)
                    .style('filter', 'drop-shadow(0 0 3px rgba(0,0,0,0.3))');

                // 高亮相关连接
                link.style('stroke', l => 
                    l.source.id === d.id || l.target.id === d.id 
                        ? '#ff9f1c' 
                        : '#999'
                )
                .style('stroke-opacity', l => 
                    l.source.id === d.id || l.target.id === d.id 
                        ? 1 
                        : 0.2
                );

                // 显示提示框
                showTooltip(event, d);
            })
            .on('mouseout', function(event, d) {
                d3.select(this).select('circle')
                    .transition()
                    .duration(300)
                    .attr('r', d => Math.sqrt(d.size) * 5)
                    .style('filter', null);

                link.style('stroke', '#999')
                    .style('stroke-opacity', 0.6);

                hideTooltip();
            });

            // 添加点击事件
            node.on('click', function(event, d) {
                if (d.type === 'post') {
                    window.location.href = `/post/${d.post_id}`;
                } else if (d.type === 'tag') {
                    window.location.href = `/tag/${d.id}`;
                }
            });

            // 创建提示框
            const tooltip = d3.select('body').append('div')
                .attr('class', 'graph-tooltip')
                .style('position', 'absolute')
                .style('visibility', 'hidden')
                .style('background', 'white')
                .style('padding', '5px 10px')
                .style('border-radius', '4px')
                .style('box-shadow', '0 2px 4px rgba(0,0,0,0.1)')
                .style('font-size', '12px')
                .style('pointer-events', 'none');

            function showTooltip(event, d) {
                const text = d.type === 'tag' 
                    ? `标签: ${d.label}<br>文章数: ${d.size}` 
                    : `文章: ${d.label}`;
                
                tooltip.html(text)
                    .style('visibility', 'visible')
                    .style('left', (event.pageX + 10) + 'px')
                    .style('top', (event.pageY - 10) + 'px');
            }

            function hideTooltip() {
                tooltip.style('visibility', 'hidden');
            }

            simulation.on('tick', () => {
                link
                    .attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y);

                node
                    .attr('transform', d => `translate(${d.x},${d.y})`);
            });

            function dragstarted(event) {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                event.subject.fx = event.subject.x;
                event.subject.fy = event.subject.y;
            }

            function dragged(event) {
                event.subject.fx = event.x;
                event.subject.fy = event.y;
            }

            function dragended(event) {
                if (!event.active) simulation.alphaTarget(0);
                event.subject.fx = null;
                event.subject.fy = null;
            }

            // 添加双击重置功能
            svg.on('dblclick', function() {
                svg.transition()
                    .duration(750)
                    .call(zoom.transform, d3.zoomIdentity);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('knowledge-graph').innerHTML = 
                '<div class="error-message">加载知识图谱失败，请刷新页面重试</div>';
        });
}); 