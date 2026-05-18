document.addEventListener('DOMContentLoaded', () => {
    const input = document.querySelector('[data-file-input]');
    const label = document.querySelector('[data-file-name]');
    if (input && label) {
        input.addEventListener('change', () => {
            label.textContent = input.files.length ? input.files[0].name : 'No file selected';
        });
    }

    document.querySelectorAll('.counter').forEach((counter) => {
        const target = Number(counter.dataset.target || '0');
        let current = 0;
        const step = Math.max(1, Math.ceil(target / 28));
        const timer = setInterval(() => {
            current = Math.min(target, current + step);
            counter.textContent = current;
            if (current >= target) clearInterval(timer);
        }, 22);
    });

    if (window.resumeStatusUrl) {
        setInterval(async () => {
            try {
                const res = await fetch(window.resumeStatusUrl);
                if (!res.ok) return;
                const data = await res.json();
                const progressBar = document.getElementById('progressBar');
                const stage = document.getElementById('stage');
                if (progressBar) progressBar.style.width = `${data.progress || 0}%`;
                if (stage) stage.textContent = data.stage || data.status || 'Processing';
                if (data.status === 'completed') window.location.reload();
            } catch (error) {}
        }, 3000);
    }
});
