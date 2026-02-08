import matplotlib.pyplot as plt

def trust_chart(trust_score):
    fig, ax = plt.subplots()
    ax.bar(["Trust Score"], [trust_score])
    ax.set_ylim(0, 1)
    ax.set_ylabel("Trust Level")
    ax.set_title("User Trust Score")
    return fig
