import os
import string

punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''

if __name__ == '__main__':
    artist_names = os.listdir('Artists_Songs')
    
    for single in artist_names:
        output=""
        filenames = os.listdir('Artists_Songs/%s'%str(single))
        for names in filenames: 
            with open('Artists_Songs/%s/%s'%(str(single),names),errors='ignore') as infile:
                data = infile.read()
                infile.close()
            output+=data

        for charc in output:
            if charc in punctuations:
                output=output.replace(charc,"")

        with open('Merged/'+str(single)+'.txt', 'w') as f: 
            f.write(output)
            f.close() 
