// BiliAnalytics - ECharts Factory Functions
// Neon anime theme for all charts

const NEON_THEME = {
    textStyle: { color: '#94a3b8' },
    backgroundColor: 'transparent',
};

function createBarChart(domId, labels, values, title) {
    const el = document.getElementById(domId);
    if (!el) return;
    const chart = echarts.init(el, 'dark');
    chart.setOption({
        title: { text: title, left: 'center', textStyle: { color: '#e2e8f0', fontSize: 14, fontWeight: 600 } },
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: '3%', right: '4%', bottom: '10%', top: '18%', containLabel: true },
        xAxis: {
            type: 'category', data: labels,
            axisLabel: { color: '#94a3b8', rotate: 30, fontSize: 10 },
            axisLine: { lineStyle: { color: 'rgba(251,114,153,0.15)' } },
        },
        yAxis: {
            type: 'value',
            axisLabel: { color: '#94a3b8', fontSize: 10 },
            splitLine: { lineStyle: { color: 'rgba(255,255,255,0.04)' } },
        },
        series: [{
            name: title, type: 'bar', data: values,
            itemStyle: {
                borderRadius: [6, 6, 0, 0],
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: '#FB7299' }, { offset: 1, color: '#FF4088' }
                ]),
            },
            emphasis: { itemStyle: { shadowBlur: 16, shadowColor: 'rgba(251,114,153,0.5)' } },
            animationDuration: 1200,
            animationEasing: 'elasticOut',
        }],
    });
    return chart;
}

function createPieChart(domId, data, title) {
    const el = document.getElementById(domId);
    if (!el) return;
    const chart = echarts.init(el, 'dark');
    chart.setOption({
        title: { text: title, left: 'center', textStyle: { color: '#e2e8f0', fontSize: 14, fontWeight: 600 } },
        tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
        series: [{
            type: 'pie', radius: ['42%', '72%'], center: ['50%', '55%'],
            avoidLabelOverlap: false,
            itemStyle: { borderRadius: 5, borderColor: 'rgba(10,10,26,0.8)', borderWidth: 2 },
            label: { show: true, color: '#94a3b8', fontSize: 10 },
            emphasis: {
                label: { fontSize: 14, fontWeight: 'bold' },
                itemStyle: { shadowBlur: 16, shadowColor: 'rgba(251,114,153,0.35)' },
            },
            data: data,
            color: ['#FB7299', '#00d4ff', '#FF6B9D', '#7C3AED', '#F59E0B', '#10B981', '#EC4899', '#3B82F6'],
            animationType: 'scale',
            animationEasing: 'elasticOut',
            animationDuration: 800,
        }],
    });
    return chart;
}

function createLineChart(domId, labels, values, title) {
    const el = document.getElementById(domId);
    if (!el) return;
    const chart = echarts.init(el, 'dark');
    chart.setOption({
        title: { text: title, left: 'center', textStyle: { color: '#e2e8f0', fontSize: 14, fontWeight: 600 } },
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '10%', top: '18%', containLabel: true },
        xAxis: {
            type: 'category', data: labels,
            axisLabel: { color: '#94a3b8', fontSize: 10 },
            axisLine: { lineStyle: { color: 'rgba(251,114,153,0.15)' } },
        },
        yAxis: {
            type: 'value',
            axisLabel: { color: '#94a3b8', fontSize: 10 },
            splitLine: { lineStyle: { color: 'rgba(255,255,255,0.04)' } },
        },
        series: [{
            name: title, type: 'line', data: values, smooth: true,
            lineStyle: { color: '#00d4ff', width: 2 },
            areaStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1, [
                { offset: 0, color: 'rgba(0,212,255,0.25)' }, { offset: 1, color: 'rgba(0,212,255,0.01)' }
            ])},
            itemStyle: { color: '#00d4ff' },
            symbol: 'circle', symbolSize: 5,
            animationDuration: 1500,
        }],
    });
    return chart;
}
