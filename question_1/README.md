**Question 1:** Which UC appears to add the most required courses when added to any pairing, and how consistent is this across different community college districts?

To answer this question we have divided it up into two sections and have two different visualizations. 

Files and what they do:

**total_number_of_courses.py
**    After inputting path to folder filled with csvs of either the community colleges or districts you want to analyze it ouputs the UC Campuses found for the CC/District along with the Number of Unique Ariticulated Courses (meaning that is the number of CC courses that can be taken to fufill requirements for all 9 UCs) and the total number of unarticlated courses.

**total_combination_order.py
**    After inputting path to folder filled with csvs of either the community colleges or districts you want to analyze it outputs two txt files and 6 csvs (which will be shown below). Before getting into the contents of these output files understanding the combination logic used is important. 
        Combination Logic:
            This script is using specifically 3 UC Combination Groups which means it groups UCs into groups of 3.
                Ex: ['UCSD' 'UCSB' 'UCLA']
            With these 3 UC Combination Pairs the script is counting how much each UC contributes to the number of courses a hypothetical UC student would need to take. That is why when 
        total_combination_order.txt
