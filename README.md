# 📊 Unraveling California's CS Transfer Pathways

<img src="https://github.com/user-attachments/assets/eae7b77a-cfa6-489c-bff6-178a7b9d9965" alt="Alvarado_Poster" width="800"/>

## 📁 Project Structure

| Folder/File        | Description |
|--------------------|-------------|
| `cc_agreements/`   | Raw articulation agreements per CC-UC pair |
| `creating_districts/` | Scripts to map colleges into districts |
| `cs_urls/`         | Generated UC-CS articulation URLs for scraping |
| `district_csvs/`   | CSVs grouping colleges by district |
| `filtered_results/`| Cleaned articulation datasets |
| `question_1/`      | Analysis for complexity of UC CS requirements |
| `question_2-3/`    | District-level coverage and missing course analytics |
| `results/`         | CSV articulation datasets for individual CCs |
| `scraping/`        | Web scraping logic (assist.org) |
---

## ⚙️ Setup Instructions

### Requirements
- Python 3.8+
- Git (optional but recommended)

## 🚀 How to Use the Project

### Step 1: Scrape Articulations
Run the scraper to organize all CC UC articulation data into CSVs
```bash
python scraping/scrape_all_cc.py
```

This will populate the `results/` folder with CSV files for each CC.

---

### Step 2: Clean & Filter Data
Run the filtering script to clean the scraped articulation data and standardize formatting.
```bash
python scraping/post_process.py
```

This will populate the `filtered_results/` folded with filtered CSV files for each CC.

---

### Step 3: Group by District
Organize colleges into their corresponding districts to analyze district-level articulation coverage.
```bash
python creating_districts/creating_district_csvs.py
```

The output will be saved in the `district_csvs/` folder.

---

### Step 4: Analyze Research Questions

#### Q1: Complexity of UC Requirements
Navigate to the `question_1/` folder and run the scripts or Jupyter notebooks to:
- Count how many CS courses each UC requires
- Identify overlapping and unique requirements

#### Q2 & Q3: District Coverage and Missing Courses
In the `question_2-3/` folder, you'll find:
- Code to calculate articulation completeness by district
- Visualizations of the most frequently unarticulated courses across UCs

---

### Step 5: View Results
Visualizations and summary data are available in the `results/` folder. These include:
- Bar charts of missing courses by UC
- Ranked list of districts by articulation coverage
- Simulated 3-UC sequences to illustrate complexity

Use these results for reporting or presentations, such as research posters.

---

## 📈 Expected Outputs

- 📊 **Unarticulated Course Charts**: Number of CS requirements not met per UC
- 🗺️ **District Maps**: Number of UCs fully supported per district
- 🔄 **3-UC Transfer Simulations**: Overlapping requirements across multiple UC application plans

---

## 📚 Background Resources

- [Assist.org](https://assist.org) – Source for articulation agreements
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Pandas Official Docs](https://pandas.pydata.org/docs/)
- [Matplotlib Tutorials](https://matplotlib.org/stable/tutorials/index.html)

---

## 👥 Team Acknowledgements

- **Advisors**: Prof. Christine Alvarado, Prof. Mia Minnes, Prof. Diba Mirza, Prof. Phill Conrad
- **Contributors**: JP Davalos, Yasmin Kabir, Brenda Ramirez, Anthony Rodriguez

---
