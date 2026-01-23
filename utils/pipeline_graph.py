import graphviz

def export_pipeline(path):
    dot = graphviz.Digraph("RAW Pipeline")
    steps = [
        "CR3",
        "Bayer",
        "Black level",
        "White balance",
        "Demosaic",
        "Color matrix",
        "Tone curve",
        "Display"
    ]

    for i in range(len(steps)-1):
        dot.edge(steps[i], steps[i+1])

    dot.render(path, format="svg")
