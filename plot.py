import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

matplotlib.use("Agg")

# Example DataFrame
data = pd.DataFrame({"x": range(10), "y": range(10)})

# Plotting
plt.figure()
plt.plot(data["x"], data["y"])
plt.savefig("static/plot.png")
