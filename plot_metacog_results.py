import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def load_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def get_color(model_name):
    model_name = model_name.lower()
    if 'claude' in model_name:
        return '#4B5ED7' # Royal Blue
    if 'gemini' in model_name:
        return '#00A170' # Emerald Green
    if 'gpt' in model_name:
        return '#FF6F61' # Living Coral / Orange-Red
    if 'deepseek' in model_name:
        return '#00BCD4' # Cyan
    return '#757575' # Grey

def setup_plot(title, xlabel='Accuracy', ylabel='M-Ratio'):
    plt.figure(figsize=(10, 8), dpi=200)
    sns.set_style("whitegrid", {'axes.grid': True, 'grid.linestyle': '--'})
    plt.title(title, fontsize=16, fontweight='bold', pad=20)
    plt.xlabel(xlabel, fontsize=12, fontweight='bold')
    plt.ylabel(ylabel, fontsize=12, fontweight='bold')
    
    # Add reference line at M-Ratio = 1.0
    plt.axhline(y=1.0, color='red', linestyle='--', alpha=0.5, label='Theoretical Efficiency (1.0)')
    
    # Highlight AGI-Aligned Region
    plt.axvspan(0.85, 1.0, ymin=0.8, ymax=1.0, color='green', alpha=0.05, label='AGI-Aligned Zone')
    
    plt.xlim(0.5, 1.05)
    plt.ylim(-0.1, 1.5)

def save_plot(filename):
    plt.legend(loc='upper left', frameon=True, fontsize=10)
    plt.tight_layout()
    plt.savefig(filename)
    print(f"Saved plot to {filename}")
    plt.close()

def main():
    data = load_data('results_aggregated.json')
    from adjustText import adjust_text
    
    # 1. Static Plot (Turn 1)
    setup_plot('Metacognitive Efficiency: Static Monitoring (Turn 1)')
    texts = []
    for model, metrics in data.items():
        static = metrics.get('static', {})
        if static:
            acc = static.get('accuracy')
            m_ratio = static.get('m_ratio')
            if acc is not None and m_ratio is not None:
                color = get_color(model)
                plt.scatter(acc, m_ratio, color=color, s=150, alpha=0.8, edgecolors='black', zorder=5)
                texts.append(plt.text(acc, m_ratio, model, fontsize=9, fontweight='bold'))
    
    if texts:
        adjust_text(texts, arrowprops=dict(arrowstyle='->', color='gray', lw=0.5))
    save_plot('plot_static_monitoring.png')

    # 2. Dynamic Plot (Turn 2)
    setup_plot('Metacognitive Efficiency: Dynamic Multi-Turn (Turn 2)')
    texts = []
    for model, metrics in data.items():
        v2 = metrics.get('multiturn_v2', {}).get('overall', {})
        if v2:
            acc = v2.get('acc')
            m_ratio = v2.get('m_ratio')
            if acc is not None and m_ratio is not None:
                color = get_color(model)
                plt.scatter(acc, m_ratio, color=color, s=150, alpha=0.8, edgecolors='black', zorder=5)
                texts.append(plt.text(acc, m_ratio, model, fontsize=9, fontweight='bold'))
    
    if texts:
        adjust_text(texts, arrowprops=dict(arrowstyle='->', color='gray', lw=0.5))
    save_plot('plot_dynamic_monitoring.png')

    # 3. Comparison Plot (Arrow Transition)
    setup_plot('The Metacognitive Capability Gap: Static → Dynamic Shift')
    texts = []
    for model, metrics in data.items():
        static = metrics.get('static', {})
        v2 = metrics.get('multiturn_v2', {}).get('overall', {})
        
        if static and v2:
            s_acc = static.get('accuracy')
            s_m = static.get('m_ratio')
            d_acc = v2.get('acc')
            d_m = v2.get('m_ratio')
            
            if all(v is not None for v in [s_acc, s_m, d_acc, d_m]):
                color = get_color(model)
                # Plot transition arrow
                plt.arrow(s_acc, s_m, d_acc - s_acc, d_m - s_m, 
                          head_width=0.008, head_length=0.012, fc=color, ec=color, 
                          alpha=0.4, length_includes_head=True, zorder=2)
                
                # Plot dynamic point (end)
                plt.scatter(d_acc, d_m, color=color, s=150, alpha=0.9, edgecolors='black', zorder=5)
                texts.append(plt.text(d_acc, d_m, model, fontsize=9, fontweight='bold'))

    if texts:
        adjust_text(texts, arrowprops=dict(arrowstyle='->', color='gray', lw=0.5))
    save_plot('plot_comparison_shift.png')

if __name__ == "__main__":
    main()
