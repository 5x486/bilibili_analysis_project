// BiliAnalytics - Canvas Danmaku Engine

class DanmakuEngine {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');
        this.danmakuList = [];
        this.running = false;
        this._resize();
        window.addEventListener('resize', () => this._resize());
    }

    _resize() {
        if (!this.canvas) return;
        this.canvas.width = this.canvas.parentElement.clientWidth || 800;
        this.canvas.height = 280;
    }

    addDanmaku(text, color) {
        if (!this.canvas) return;
        const colors = ['#FB7299', '#00d4ff', '#FF6B9D', '#7C3AED', '#F59E0B', '#10B981', '#FFD700', '#EC4899'];
        const c = color || colors[Math.floor(Math.random() * colors.length)];
        this.danmakuList.push({
            text: text, x: this.canvas.width, y: Math.random() * (this.canvas.height - 40) + 20,
            color: c, speed: 1.4 + Math.random() * 1.8, opacity: 0.65 + Math.random() * 0.3,
        });
    }

    start(interval) {
        if (!this.canvas || this.running) return;
        this.running = true;
        const texts = ['23333', '666', '前方高能', 'awsl', '名场面', '打卡', '泪目', '好评',
            'xswl', '有生之年', '真实', 'hhh', '牛批', '高能预警', '卧槽'];
        this._timer = setInterval(() => {
            if (!this.running) return;
            this.addDanmaku(texts[Math.floor(Math.random() * texts.length)]);
        }, interval || 350);
        this._render();
    }

    stop() {
        this.running = false;
        if (this._timer) clearInterval(this._timer);
    }

    _render() {
        if (!this.running || !this.canvas) return;
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.danmakuList = this.danmakuList.filter(d => d.x > -300);
        this.danmakuList.forEach(d => {
            this.ctx.save();
            this.ctx.globalAlpha = d.opacity;
            this.ctx.font = 'bold 17px "Noto Sans SC", system-ui, sans-serif';
            this.ctx.fillStyle = d.color;
            this.ctx.shadowColor = d.color;
            this.ctx.shadowBlur = 5;
            this.ctx.fillText(d.text, d.x, d.y);
            this.ctx.restore();
            d.x -= d.speed;
        });
        requestAnimationFrame(() => this._render());
    }
}
