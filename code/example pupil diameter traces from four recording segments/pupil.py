import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os

# ===== Set fonts =====
plt.rcParams["font.family"] = "Calibri"
plt.rcParams["font.sans-serif"] = ["Calibri"]
plt.rcParams["axes.unicode_minus"] = False

sns.set_theme(
    style="whitegrid",
    font="Calibri",
    font_scale=1.1
)

# ===== Adjust global font sizes =====
plt.rcParams['font.size'] = 30
plt.rcParams['axes.labelsize'] = 32
plt.rcParams['axes.titlesize'] = 34
plt.rcParams['xtick.labelsize'] = 30
plt.rcParams['ytick.labelsize'] = 30
plt.rcParams['legend.fontsize'] = 25
plt.rcParams['figure.titlesize'] = 36



# ===== Define the list of allowed question numbers =====
allowed_questions = {
    6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,34,35,36,75,76,91,
    23,24,41,42,43,44,45,46,47,48,49,50,51,52,53,
    25,26,27,37,38,39,40,78,79,80,81,85,86,90,92,95,
    28,29,30,31,89,94,96,
    32,33,82,83,84,87,88,93,
    55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116
}

# ===== Read the TSV file =====
file_path = 'data/pupil.tsv'
df = pd.read_csv(file_path, sep='\t', low_memory=False)
print(f"Total rows in the raw data:{len(df)}")

# ===== Filter data =====
df = df[df['Sensor'] == 'Eye Tracker'].copy()
print(f"Rows after filtering for Eye Tracker:{len(df)}")

def extract_question_number(name):
    if pd.isna(name):
        return None
    match = re.search(r'(\d+)', str(name))
    if match:
        return int(match.group(1))
    return None

df['Question_Number'] = df['Presented Media name'].apply(extract_question_number)
df = df[df['Question_Number'].isin(allowed_questions)].copy()
print(f"Rows after matching valid question numbers:{len(df)}")

if df.empty:
    print("No valid question numbers matched. Exiting.")
    exit()

# ===== Determine validity =====
df['Validity left'] = df['Validity left'].astype(str).str.strip()
df['Validity right'] = df['Validity right'].astype(str).str.strip()

valid_mask = (
    (df['Validity left'] == 'Valid') &
    (df['Validity right'] == 'Valid') &
    df['Pupil diameter left'].notna() &
    df['Pupil diameter right'].notna() &
    df['Pupil diameter filtered'].notna()
)
df['is_valid'] = valid_mask

all_question_nums = df['Question_Number'].unique()
print(f"Number of unique question numbers: {len(all_question_nums)}")

# ===== Generate validity-proportion ranking table =====
print("\nGenerating the validity-proportion ranking table...")
grouped_stats = df.groupby('Question_Number').agg(
    Total_Records=('is_valid', 'count'),
    Valid_Records=('is_valid', 'sum')
).reset_index()

grouped_stats['Validity_Proportion'] = grouped_stats['Valid_Records'] / grouped_stats['Total_Records']
ranked_table = grouped_stats.sort_values('Validity_Proportion', ascending=False).reset_index(drop=True)
ranked_table.index = ranked_table.index + 1
ranked_table = ranked_table.rename_axis('Rank').reset_index()
ranked_table['Invalid_Records'] = ranked_table['Total_Records'] - ranked_table['Valid_Records']
ranked_table = ranked_table[['Rank', 'Question_Number', 'Total_Records', 'Valid_Records', 'Invalid_Records', 'Validity_Proportion']]

print("\n========== Validity-proportion ranking for all question numbers ==========")
print(ranked_table.head(20).to_string(index=False))
print(f"\n... {len(ranked_table)} question numbers in total")

ranked_table.to_csv('pupil_data_validity_proportion_ranking.csv', encoding='utf-8-sig', index=False)
print("\nFull ranking table saved to 'pupil_data_validity_proportion_ranking.csv'")

# ===== Generate line plots for all question numbers =====
output_dir = 'pupil_plots_all'
os.makedirs(output_dir, exist_ok=True)

plot_count = 0
for q_num in sorted(all_question_nums):
    data_subset = df[df['Question_Number'] == q_num].sort_values('Recording timestamp')
    if data_subset.empty:
        continue

    valid_data = data_subset[data_subset['is_valid']]
    if valid_data.empty:
        print(f"Question {q_num} has no valid data; skipping")
        continue

    # Calculate the y-axis range using the minimum/maximum valid values plus margins
    valid_vals = pd.concat([
        valid_data['Pupil diameter left'],
        valid_data['Pupil diameter right'],
        valid_data['Pupil diameter filtered']
    ])
    lower = valid_vals.min()
    upper = valid_vals.max()
    if upper - lower > 1e-6:
        margin = (upper - lower) * 0.05
    else:
        margin = 0.5
    y_min = lower - margin
    y_max = upper + margin

    plt.figure(figsize=(14, 7))
    time_sec = data_subset['Recording timestamp'] / 1000.0

    plt.plot(time_sec, data_subset['Pupil diameter left'],
             label='Left', color='#6BAED6', linewidth=1.6, alpha=0.85)   # Soft blue
    plt.plot(time_sec, data_subset['Pupil diameter right'],
             label='Right', color='#FDD070', linewidth=1.6, alpha=0.85)  # Soft yellow
    plt.plot(time_sec, data_subset['Pupil diameter filtered'],
             label='Filtered', color='#74C476', linewidth=2.0, alpha=0.9) # Soft green

    plt.xlabel('Recording Timestamp (s)')
    plt.ylabel('Pupil Diameter (mm)')
    plt.legend(
        loc='upper right',
        labelspacing=0,
        borderpad=0.2,
        handlelength=1.2,
        handletextpad=0.4,
        borderaxespad=0.1,
        framealpha=0.2
    )

    plt.grid(True, alpha=0.3)
    plt.ylim(y_min, y_max)
    plt.tight_layout()

    filename = f'pupil_question_{q_num}.png'
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    plot_count += 1
    if plot_count % 10 == 0:
        print(f"Generated {plot_count} images...")

print(f"\nAll plots generated. Created {plot_count} images in the '{output_dir}' folder.")