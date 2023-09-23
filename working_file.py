#!/usr/bin/python3

import logging
import pandas as pd
from reportlab.pdfgen import canvas

import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
#import matplotlib.pyplot as plt





# Set up the logging configuration
logging.basicConfig(filename='log.txt', level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')

# Get the script name and author
script_name = "Grademaster Tool"
script_version="v2.1"
author = 'Sakthi Aadharsh Azhagar Gobinath Kavitha'
changes= 'UI update - plots update'
# Log the script name and author
logging.info(f'Starting script: {script_name},Script version: {script_version}, Author: {author}, Changes:{changes}')



def percent2grade(percent):
    if percent >= 96:
        return "A"
    elif percent >= 91:
        return "A-"
    elif percent >= 86:
        return "B+"
    elif percent >= 81:
        return "B"
    elif percent >= 76:
        return "B-"
    elif percent >= 71:
        return "C+"
    elif percent >= 66:
        return "C"
    elif percent >= 61:
        return "C-"
    elif percent >= 56:
        return "D+"
    elif percent >= 51:
        return "D"
    else:
        return "F"
def mark2percent(students):
    row_sum=(students.sum(axis=1))
    num_cols = len(students.columns)
    return row_sum/num_cols

    
# Input
df = pd.read_csv('grade_dummy_file2_v2.csv')
df= df.dropna(axis='columns')
# set 'Student' as the index column
df.set_index('First name', inplace=True)


# create a DataFrame with only the students (A, B, C) and the weights (W)
students = df.loc[ :df.index[-1] , 'HW1':]
print(students.index)
roll_no=df['Student ID'].tolist()
lastname=df['Last name'].tolist()


# multiply the students DataFrame by the weights Series and create a new column for the total
students['Total'] =mark2percent(students)
students["Last Name"]=df.loc[ :df.index[-1] ,'Last name']
# create a list of the total calculated for A to E (not W)
total_student = students['Total'].tolist()
#percentile calculation
students['Percentile'] = students['Total'].rank(pct=True) * 100
#print(students)
percentiles = students['Percentile'].tolist()
students["Grade"] = students["Total"].apply(percent2grade)
# Rank  Calculation
rank=students.sort_values('Total',ascending=[False])
students['Rank']=students['Total'].rank(ascending=False)

print(students)
# Convert the 'Rank' column to a list of tuples (index, rank)
rank_list = [(index, rank) for index, rank in students['Rank'].items()]

# Sort the list based on the rank value (second element)
sorted_rank_list = sorted(rank_list, key=lambda x: x[1])

# Print the sorted rank list
stud =[]
for index, rank in sorted_rank_list:
    stud.append((index,rank))


# Statistical parameters
stats=students.describe().round(2)

#Printing the results
for i in range(len(total_student)):
        #print("Student "+str(df.index[i]))
        grade=percent2grade(total_student[i])
        #print("The percentage is " + str(total_student[i])+"%")
        grade=percent2grade(total_student[i])
        #print("The grade is "+str(grade))
        #print("The percentile is "+str(percentiles[i]))
        
class jump_next_line:
    def __init__(self, value):
        self.value = value
    
    def __getattribute__(self, name):
        value = object.__getattribute__(self, 'value')
        if name == 'value':
            value -= 10
            object.__setattr__(self, 'value', value)
        return value


# output to pdf
## Teacher's copy
margin = 100
centre = 250 
line = jump_next_line(800)
teacher_pdf = canvas.Canvas("teachers.pdf")
teacher_pdf.setFont("Helvetica-Bold", 16)
teacher_pdf.drawString(centre, line.value - 20, "Teacher's Copy")
## rank


margin = 100
centre = 250 
line = jump_next_line(800)

teacher_pdf.setFont("Helvetica-Bold", 14)
teacher_pdf.drawString(centre, line.value - 60, "Rank details (Top 20)")
q=0

max_name_length = max(len(entry[0]) for entry in stud)
max_rank_length = max(len(str(entry[1])) for entry in stud)
w=line.value
for i, entry in enumerate(stud):
    if i <20 :
        w+=1
    else:
        break
       

    name_padding = max_name_length - len(entry[0]) + 2
    rank_padding = max_rank_length - len(str(entry[1])) + 2

    teacher_pdf.drawString(centre, w- 120 - i * 30, f"{entry[0]:<{max_name_length}} {entry[1]:<{max_rank_length}}")

teacher_pdf.showPage()
##
teacher_pdf.setFont("Helvetica-Bold", 14)
teacher_pdf.drawString(centre, line.value - 60, "Statistics")

stats = stats.T
stat = stats.loc['HW1':'Total', 'mean':'min']
stat['max'] = stats['max']
stats=stat.T

means = stats.loc['mean']
stat=str(stat)

# Split the string by lines
lines = stat.strip().split('\n')

# Extract the column headers by splitting the first line
headers = lines[0].split()
headers.insert(0, 'Assignment')
# Initialize an empty dictionary to store the parsed data
data = {}

# Process each subsequent line and extract the values
for l in lines[1:]:
    # Split the line and remove any leading/trailing whitespaces
    values = l.split()
    values = [value.strip() for value in values]
    
    # Extract the key (e.g., HW1, HW2, etc.)
    key = values[0]
    
    # Convert the numeric values from strings to floats
    numeric_values = [float(value) for value in values[1:]]
    
    # Assign the key-value pair to the dictionary
    data[key] = numeric_values


# Draw the table
teacher_pdf.setFont("Helvetica", 12)
c= line.value
for i, header in enumerate(headers):
    
    teacher_pdf.drawString(margin + i * 100, c - 90, header)
    

teacher_pdf.setFont("Helvetica", 12)
for i, (key, values) in enumerate(data.items()):
    c=line.value
    teacher_pdf.drawString(margin, c - 120 - i * 30, key)
    for j, value in enumerate(values):
        teacher_pdf.drawString(margin + (j + 1) * 100, c - 120 - i * 30, f"{value:.2f}")
teacher_pdf.showPage()



# Plot the statistics as a bar chart
means.plot(kind='bar')
plt.title('Mean Values')
plt.xlabel('Columns')
plt.ylabel('Mean')


# Save the chart as an image in memory
plot_buffer = BytesIO()
plt.savefig(plot_buffer, format='png')
plt.close()

# Draw the chart image on the PDF canvas
image = ImageReader(plot_buffer)
teacher_pdf.drawImage(image, 100, 300, width=400, height=300)

# Save the PDF file
teacher_pdf.save()

# student copy
columns = ['Last Name']

for i in range(len(roll_no)):
    print(i)
    margin = 100
    centre = 150 
    line = jump_next_line(800)
    student_pdf = canvas.Canvas(f"student_{roll_no[i]}.pdf")
    student_pdf.setFont("Helvetica-Bold", 16)
    student_pdf.drawString(centre+70, line.value - 20, "Progress Report")
    student_pdf.setFont("Helvetica-Bold", 14)
    student_pdf.drawString(centre+65, line.value - 60, "Personal Information")
    y=line.value - 20
    student_pdf.setFont("Helvetica", 12)
    L=line.value - 60
    student_pdf.drawString(margin+10, L, f"Name: {students.index[i]} {students['Last Name'][i]}")
    student_pdf.drawString(margin+300, L, f"Roll no: {df['Student ID'][i]}")
    student_pdf.drawString(margin+10, L-20, f"Rank: {students['Rank'][i]}")
    student_pdf.drawString(margin+300, L-20, f"Percentile: {round(students['Percentile'][i], 2)}")
    student_pdf.drawString(margin+150, L-20, f"Grade: {students['Grade'][i]}")
    student_name = students.index[i]
    hw_scores = students.loc[students.index[i] ,'HW1':'HW10']
    means.plot(kind='line')
    plt.title(f"{students.index[i]} {students['Last Name'][i]}")
    plt.xlabel("Assignments")
    plt.ylabel('Score')
    # Save the plot as a separate image file
    plot_buffer = BytesIO()
    plt.savefig(plot_buffer, format='png')
    plt.close()
    
    image = ImageReader(plot_buffer)
    student_pdf.drawImage(image, 100, 300, width=400, height=300)

    # Draw the chart image on the PDF
    student_pdf.save()

print("Program Terminated Successfully!! Please check the output files. Thank you!!")       
logging.info('Script finished.')