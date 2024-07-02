import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

matplotlib.use("Agg")

# Load your data
df = pd.read_csv("your_data.csv")  # Replace with your actual data source

# Filter the DataFrame for Engagement Status = "Released"
df_filtered = df[df["Engagement Status"] == "Released"]

# Calculate service line counts
service_line_counts = df_filtered["Engagement Partner Service Line"].value_counts()

# Set the aesthetic style of the plots
sns.set(style="whitegrid")

# Create the plot
plt.figure(figsize=(10, 6))
sns.barplot(
    x=service_line_counts.values, y=service_line_counts.index, palette="viridis"
)
plt.title("Service Line Counts for Released Engagements", fontsize=16)
plt.xlabel("Count", fontsize=14)
plt.ylabel("Service Line", fontsize=14)
plt.tight_layout()

# Save the plot as an image
plt.savefig("static/plot.png")
