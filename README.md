# Wedding Invitation Stamper 2

This Python GUI app is used for stamping names and table number on wedding invites, either only on the first page (*stamp_invites.py*) resulting in a png, or on a first page and prepending this page to the details.pdf in the utils folder (*stamp_invites_pdf.py*).

The positions, font, sizes and colors of text can be adjusted via the GUI.


# Usage

1- Install Python 3.14

2- Install dependencies
    `sh
    pip install -r requirements.txt
    `

3- Add guest list in guest_list.csv

4- Place the first page of your invite in *utils/invitation.png*

5- If you need only the first page stamped, run
    `sh 
    python stamp_invites.py
    `

6- If you need to add the remaining pages and generate a pdf, place the pdf containing the remaining pages of your invite in utils/details.pdf and run
    `sh 
    python stamp_invites_pdf.py
    `
The invites will be saved to the invites folder. 

You can adjust the stamped text via the GUI and regenerate the invites.
