
class ExtractPDf():
    def __init__(self, file_path, countries):
        self.file_path = file_path
        self.countries = countries

    def check_no(self, no_index, entry):
        no = entry[no_index]
        list_no = no.split()
        if len(''.join(list_no))>36:
            print('Warning: ID No too long!')
            no = ''
        elif len(''.join(list_no))<6:
            print('Warning: ID No too short!')
            no = ''
        else:
            if len(list_no)>1:
                if len(list_no[-1])<3:
                    list_no[-2] = list_no[-2]+list_no[-1]
                    list_no = list_no[:-1]
                len_list = [len(d) for d in list_no]
                if 1 in len_list:
                    idx = len_list.index(1)
                    if idx == 0:
                        print('Error: first part of ID No is one element!')
                    else:
                        list_no[idx-1] = list_no[idx-1] + list_no[idx]
                        list_no.pop(idx)
                        print(f'new list:{list_no}')
                no = ' '.join(list_no)
            else:
                l = len(no)
                if l > 21:
                    # three id no
                    n = l // 3
                    mod = l % 3
                    if mod in [0,1]:
                        no = no[:n] + ' ' + no[n:2*n] + ' ' + no[2*n:]
                    elif mod ==2:
                        no = no[:n] + ' ' + no[n:2*n+1] + ' ' + no[2*n+1:]
                elif l> 12:
                    if l % 2 == 0:
                        n = l//2
                        no = no[:n]+ no[n:]
                
        entry[no_index] = no    
        return entry
    

    def locate_end_of_line(self,num_dates, remaining_text):
        date_pattern = r'\d{1,2}\s[A-Za-z]{3}\s\d{4}'
        ending_str = ''
        min_len_date = 10
        date_format = "%d %b %Y"
        count = 0
        match = re.search(r'\d', remaining_text)
        if match:
            start_idx = match.start()
            # print(f'start_idx:{start_idx}')
        if start_idx and len(remaining_text)-start_idx-1 > min_len_date:
            start_time = time.time()
            
            for i in range(min_len_date, len(remaining_text)):
                
                s = remaining_text[start_idx:start_idx+i]
                # print(f's:{s}')
                match = re.search(date_pattern, s)
                if match:
                    date_str = match.group()
                    # print(f"Found date: {date_str}")
                    # check if it is valid time
                    try:
                        date_obj = datetime.strptime(date_str, date_format)
                        result = 1
                    except ValueError:
                        result = 0
                        continue

                    if result == 1 and count < num_dates:
                        count += 1
                        ending_str = ending_str + ' ' + date_str
                        start_idx = remaining_text.find(date_str) + len(date_str)
                    
                if count == num_dates:
                    break
                end_time = time.time()
                if end_time - start_time > 10:
                    print('Takes too long! Stop!')
                    break
                            
            
            
        
        else:
            print('length of remaining text is too short!')
        
        if count == num_dates:
            
            idx = remaining_text.find(ending_str)
            print(f'ending_idx:{idx}')
            if idx != -1:
                remaining_text = remaining_text[idx+len(ending_str):].strip()
            else:
                x = ending_str[:11]
                start_idx = remaining_text.find(x)
                remaining_text = remaining_text[start_idx+len(x):].strip()
                for j in ending_str[11:]:
                    if j != ' ':
                        remaining_text = remaining_text.replace(j, '',1)
                
        else:
            remaining_text = ''
        
        return remaining_text, ending_str
    

    def get_txt_lines(self, txt_dir, file_name):
        txt_name = Path(os.path.basename(file_name)).with_suffix('.txt')
        txt_path = os.path.join(txt_dir, txt_name)
        lines = []
        # Check if the file exists
        if os.path.exists(txt_path):
            with open(txt_path, 'r') as file:
                lines = file.readlines()
        return txt_path, lines
    


    def retrieve_name(self, lines, name_kwd, confirm_wd_1, confirm_wd_2): 
        # for those address doesn't start with numbers
        name = ''
        for i in range(len(lines)):
            line = re.sub(r'/', '', lines[i])
            if i + 1 < len(lines):
                line_1 = re.sub(r'/', '', lines[i+1])
                # print(f'line_1:{line_1}')
                if i + 2 < len(lines):
                    line_2 = re.sub(r'/', '', lines[i+2])
                    # print(f'line_2:{line_2}')
            index = line.find(name_kwd)
            if index != -1:
                if confirm_wd_1 in line or confirm_wd_1 in line_1 :
                    if confirm_wd_2 in line or confirm_wd_2 in line_1  or confirm_wd_2 in line_2:
                        # name = line 
                        print(f'first line: {line}')
                        idx = line.find(name_kwd)
                        name = line[idx:]
                        print(f'name according to first line:{name}')
                        # problem: sometimes the name is more than 1 row
                        if lines[i+1][0] == '(': # maybe lines[i+2]?
                            for j in range(i+1, i+5):
                                if ')' in lines[j]:
                                    # end_line_index = j
                                    name = [lines[x] for x in range(i,j+1)]
                                    name = " ".join(name).strip()
                    name = re.sub('\n', ' ', name)
                    name = re.sub('\s+', ' ', name)
                    name = re.sub(r'/', '', name)

            else:
                continue
        return name
    

    def retrieve_name_addr(self, file_path, pdf_index, row_index, df):
        name = ''
        address = ''
        print(f'pdf_index:{pdf_index}, row_index: {row_index}')
        # Check if the file exists
        if os.path.exists(file_path):
            print('File existed')
            with open(file_path, 'r') as file:
                lines = file.readlines()
            # locate the keyword in df to know the name
            target = df[df['pdf index']==pdf_index].loc[row_index, 'Name']
            print(f'target:{target}')
            if len(target.split()) > 0:
                kwd = target.split()[0]
                if len(target.split()) > 1:
                    confirm = target.split()[1]
                    print(f'kwd:{kwd}')
                    for i in range(len(lines)):
                        line = lines[i]
                        if kwd in line:
                            if confirm in line or confirm in lines[i+1]:
                                name = line
                                print(f'name:{name}')
                                # save the change into df
                                # df[df['pdf index']==pdf_index].loc[row_index, 'Name'] = name
                                if len(name.split()) > 1:
                                    x = name.split()[-1]
                                    index = target.find(x)
                                    if index != -1:
                                        address = target[index + len(x):].strip()
                                        print(f'address:{address}')
                                        # df[df['pdf index']==pdf_index].loc[row_index, 'Address'] = address
                                else:
                                    index = target.find(name)
                                    address = target[index + len(name)].strip()
                                    print(f'address:{address}')
                                    # df[df['pdf index']==pdf_index].loc[row_index, 'Address'] = address  
                                break
        else:
            print("No matching file found.")
        return  name, address
    


    def split_pdf_subfolders(self, pdf_folder, subfolder_base, num_pdf_subfolder):
        subfolder_path = []
        subfolder_base.mkdir(parents=True, exist_ok=True)  # Create base folder if it doesn't exist

        pdf_files = [file for file in pdf_folder.iterdir() if file.suffix.lower() == '.pdf']

        subfolder_count = 1
        file_count = 0
        subfolder_name = f'subfolder_{subfolder_count}'
        current_subfolder = subfolder_base / subfolder_name
        current_subfolder.mkdir(exist_ok=True)
        subfolder_path.append(current_subfolder)

        for i,file in enumerate(pdf_files):
            shutil.copy(str(file), current_subfolder / file.name)
            file_count += 1

            if file_count >= num_pdf_subfolder and i < len(pdf_files)-1:  
                subfolder_count += 1
                file_count = 0
                subfolder_name = f'subfolder_{subfolder_count}'
                current_subfolder = subfolder_base / subfolder_name
                current_subfolder.mkdir(exist_ok=True)
                subfolder_path.append(current_subfolder)

        print(f'Successfully moved {len(pdf_files)} PDF files into {subfolder_count} subfolders.')
        return subfolder_path
    

    def read_pdf_into_text(self, pdf_folder, txt_dir):
        pdf_date_list = []
        comp_name_list = []
        file_list = []
        company_info_list = []
        share_captical_list = []
        prob_associates_list = []
        curr_appt_holder_list = []
        curr_share_holder_list = []
        past_appt_holder_list = []
        text_list = [company_info_list, share_captical_list, prob_associates_list, curr_appt_holder_list, curr_share_holder_list, past_appt_holder_list]

        # print(f'iterdir:{pdf_folder.iterdir()}')
        for file in pdf_folder.iterdir():
            # print(f'file:{file.name}')
            if file.suffix == ".pdf":
                file_list.append(file)
                with open(file, 'rb') as pdf_file:
                    reader = PyPDF2.PdfReader(pdf_file)
                    text = ''
                    for page in reader.pages:
                        text += page.extract_text()  # Extract text from each page

                name = file.name
                output_path = txt_dir / name
                output_path = output_path.with_suffix('.txt')
                
                # basic cleaning (front) --done (recover later)
                front_token = 'ENTITY PROFILE REPORT\s*(.*?)\s*(.*?)\s*Created by: oiada\s*Private & Confidential\s*Page\s\d\s*of\s*\d+\W*'
                text = re.sub(front_token, ' ', text).strip()
                print(text[:20], 'finished!')
                # Write the extracted text to a .txt file
                with open(output_path, 'w') as text_file:
                    text_file.write(text)

                # remove/split explanatory notes (repeated probable associates)
                split_text = re.split(r'(EXPLANATORY NOTES)', text, maxsplit=1)
                new_text = split_text[0]
                break_pattern = r'(COMPANY INFORMATION|SHARE CAPITAL|PROBABLE ASSOCIATES|CURRENT APPOINTMENT HOLDERS|CURRENT SHAREHOLDERS|PAST APPOINTMENT HOLDERS|PAST SHAREHOLDERS|CURRENT CHARGES|PAST CHARGES|EXPLANATORY NOTES)'
                sections = re.split(break_pattern, new_text)
                sections = [section.strip() for section in sections if section.strip()]
                # extract name and date
                pattern_front = r'(.+)\s+(\d+\s+\w+\s+\d+)\s+RED\s+SCORE\s+NETWORK\s+SCORE'
                result = re.search(pattern_front, sections[0])
                company_name = result.group(1)
                pdf_date = result.group(2)
                comp_name_list.append(company_name)
                pdf_date_list.append(pdf_date)
                # print(f'company_name:{company_name}, pdf_date:{pdf_date}')

                for i in range(len(sections)):
                    section = sections[i]
                    if i % 2 == 0:
                        j = int(i/2 - 1)
                        # print(f'one section:\n {section} \n finsihed! \n' )
                        if j != 2 and  -1 < j <6:
                            text_list[j].append(section)
                        # print(f'{j}th of textlist:\n {section}')

        print(f'Finish writing {len(file_list)}text file')
        return text_list, file_list
    


    def extract_company_info(self, exl_name, text_list):
        company_info_df = pd.DataFrame(columns = ['Type', 'Effective Date', 'Other names', 'Country', 'Incorporation Date', 'Social Credit Number', 'Regist No', 'ID type', 'Regist Addr', 'PBAC', 'PBA', 'SBAC', 'SBA', 'Status', 'Ownership Layers'])
        for i in range(len(text_list[0])):
            text = text_list[0][i]
            new_text = re.sub(r'\n+', ' ', text)
            # print(new_text)
            info_pattern =  r'Type\s*:(.+?)Effective Date of Current Name\s*:(.+?)Former\s*\/\s*Other Name\(s\)\s*\(Effective Date\)\s*:(.+?)Country\s*\/\s*Region of Incorporation\s*\/\s*Registration\s*:(.+?)Incorporation Date\s*:(.+?)Social Credit Number\s*:(.+?)Company Registration No.\s*:(.+?)ID Type\s*:(.+?)Registered Address\s*:(.+?)Primary Business Activity Code\s*:(.+?)Primary Business Activity\s*:(.+?)Secondary Business Activity Code\s*:(.+?)Secondary Business Activity\s*:(.+?)Status\s*:(.+?)Ownership Layers\s*:(.+)'
            info_results = re.findall(info_pattern, text, re.DOTALL)
            new_row_df = pd.DataFrame(info_results, columns=company_info_df.columns)
            # Concatenate the new row with the existing DataFrame
            company_info_df = pd.concat([company_info_df, new_row_df], ignore_index=True)

        company_info_df.to_excel(exl_name, index=False, engine='openpyxl')
        print('Finish extracting company information!')


    def extract_share_capital(self, exl_name, text_list):
        share_capital_df = pd.DataFrame(columns = ['Type', 'Currency', 'Issued shares', 'Issued capital'])
        for i in range(len(text_list[1])):
            text_1 = text_list[1][i] 
            # print('first pdf share capital part:\n', text_1)
            share_capital_pattern =  r'SHARE TYPE\s*CURRENCY\s*ISSUED SHARES\s*ISSUED CAPITAL\s*(.+)'
            share_cap_match = re.search(share_capital_pattern, text_1)
            if share_cap_match:
                share_cap_results = share_cap_match.group(1)
                # print('share_cap_results:\n', share_cap_results)
                seg_share_cap_results = re.split(r'\s+', share_cap_results)
                # print(seg_share_cap_results)
                if len(seg_share_cap_results) == 4:
                    share_cap_df = pd.DataFrame([seg_share_cap_results], columns = share_capital_df.columns)
                elif len(seg_share_cap_results) == 5:
                    seg_share_cap_results = [seg_share_cap_results[0]+ ' ' + seg_share_cap_results[1], seg_share_cap_results[2], seg_share_cap_results[3], seg_share_cap_results[4]]
                    share_cap_df = pd.DataFrame([seg_share_cap_results], columns = share_capital_df.columns)
                else:
                    print(f'Error in extracting SHARE CAPITAL of {i} th pdf, the segmented content is {seg_share_cap_results}')
                    share_cap_df = [['NAN']*4]
            else:
                print('No matching result!')
                share_cap_df = [['NAN']*4]

            share_capital_df = pd.concat([share_capital_df, share_cap_df], ignore_index=True)

        share_capital_df.to_excel(exl_name, index=False, engine='openpyxl')
        print('Finish extracting share capital!')


    def entry_curr_appt(self, text_3, pdf_index, file_list, txt_dir):

        flag = 0 # 0: have remaining text -> continue extracting
        remaining_text = ''
        name = address = No = ID_type = ctry = pos = appt_date = disc_date = ''
        check_entry = []

        if len(text_3)>5:
            file_name = file_list[pdf_index]
            txt_path, lines = self.get_txt_lines(txt_dir, file_name)
            text_3 = text_3.strip()
            name_kwd = text_3.split()[0]
            print(f'name_kwd:{name_kwd}')
            if name_kwd != '-':
                confirm_wd_1 = text_3.split()[1].strip()
                print(f'confirm_wd_1:{confirm_wd_1}')
                confirm_wd_2 = text_3.split()[2].strip()
                print(f'confirm_wd_2: {confirm_wd_2}')
                name = self.retrieve_name(lines, name_kwd, confirm_wd_1, confirm_wd_2)
                print(f'retrived name: {name}')
                conde_name = name.replace('(', ' ').replace(')', ' ')
                conde_name = re.sub('\s+', ' ', conde_name)
                print(f'condemned name:{conde_name}')
                index = text_3.find(conde_name)
                
                
                if index != -1:
                    text_3= text_3[index+len(conde_name):].strip()
                    print(f'text_3:{text_3}')
            else:
                flag = 1


        # address: 
        # special those without 6 digits end
        # Q: which way is more accurate -- first search for country or not (if not, after using 6 digits need to check)?
        if name and len(text_3) > 5:
            start_index = 0
            end_index = 0
            len_addr = min(150, len(text_3)-5)
            origin_text_3 = text_3
            country = ''
            for i in range(len_addr):
                # method 1: perform country check first on length i (if not have the address by default?)
                
                s = text_3[:i+1]
                ctry = [country for country in self.countries if country in s]
                # ctrys = [country for country in s if country in countries]
                if ctry:
                    country = ctry[-1]
                    print(f'new country in address, potential country of address: {country}')

                    # first country name is SG: assume this is SG address -> check 6 digits end (seems repeated)
                    if country == 'SINGAPORE':
                        idxes = [match.start() for match in re.finditer(country,s)]
                        for idx in idxes:
                            if len(s) >= idx+16 and s[idx+len(country)]==' ' and s[idx+len(country)+1:idx+len(country)+7].isdigit():
                                print('Confirmed: Singapore address with 6 digits end!')
                                address = s[:idx+16].strip()
                                text_3 = text_3[idx+16:].strip()
                                break
                        if address:
                            break

                    # elif country == ' IL' and i < 10:
                    #     continue

                        
                                
                    # first country name not SG: 1) Singapore addr(excluded); 2)foreign addr
                    else:
                        idx = s.find(country)
                        related_countries = [item for item in countries if country in item]
                        idxes = [text_3[:i+10].find(c) + len(c) - 1 for c in related_countries]
                        country = related_countries[idxes.index(max(idxes))]
                        idx = text_3.find(country)
                        checked_text_3 = text_3[i+1:i+5].replace(' ', '')


                        if country == 'CHINA' and text_3[idx+len(country)] == ' ' and text_3[idx+len(country)+1:idx+len(country)+7].isdigit(): 
                            address = text_3[:idx+len(country)+7].strip()
                            text_3 = text_3[idx+len(country)+7:].strip()
                            break

                        elif country in [ ' USA','U.S.A.','U.S.A', 'U S A', ' US'] and text_3[idx+len(country)] == ' ' and text_3[idx+len(country)+1:idx+len(country)+6].isdigit(): 
                            if text_3[idx+len(country)+6] == '-':
                                if text_3[idx+len(country)+7:idx+len(country)+11].isdigit():
                                    address = text_3[:idx+len(country)+11].strip()
                                    text_3 = text_3[idx+len(country)+11:].strip()
                                    break
                            else:
                                address = text_3[:idx+len(country)+6].strip()
                                text_3 = text_3[idx+len(country)+6:].strip()
                                break

                        elif country in ['AUSTRALIA', ' AUST'] and text_3[idx+len(country)] == ' ' and text_3[idx+len(country)+1:idx+len(country)+5].isdigit(): 
                            address = text_3[:idx+len(country)+5].strip()
                            text_3 = text_3[idx+len(country)+5:].strip()
                            break

                        elif country == 'SOUTH AFRICA' and text_3[idx+len(country)] == ' ' and text_3[idx+len(country)+1:idx+len(country)+5].isdigit(): 
                            address = text_3[:idx+len(country)+5].strip()
                            text_3 = text_3[idx+len(country)+5:].strip()
                            break

                        elif country in ['JANPAN', ' JPN'] and text_3[idx+len(country)] == ' ' and text_3[idx+len(country)+1:idx+len(country)+4].isdigit() and text_3[idx+len(country)+4] =='-' and text_3[idx+len(country)+5:idx+len(country)+9].isdigit(): 
                            address = text_3[:idx+len(country)+7].strip()
                            text_3 = text_3[idx+len(country)+7:].strip()
                            break

                        elif country[:6] == 'TAIWAN' and text_3[idx+len(country)] == ' ' and text_3[idx+len(country)+1:idx+len(country)+7].isdigit(): 
                            address = text_3[:idx+len(country)+7].strip()
                            text_3 = text_3[idx+len(country)+7:].strip()
                            break
                            
                        elif country == ' IL ' and text_3[idx+len(country):idx+len(country)+5].isdigit():
                            address = text_3[:idx+len(country)+5].strip()
                            text_3 = text_3[idx+len(country)+5:].strip()
                            break
                        
                        elif country == 'THAILAND' and text_3[idx+len(country)] == ' ' and text_3[idx+len(country)+1:idx+len(country)+6].isdigit():
                            address = text_3[:idx+len(country)+6].strip()
                            text_3 = text_3[idx+len(country)+6:].strip()
                            break

                        elif country in ["M'SIA", "MALAYSIA"] and text_3[idx+len(country)] == ' ' and text_3[idx+len(country)+1:idx+len(country)+6].isdigit():
                            address = text_3[:idx+len(country)+6].strip()
                            text_3 = text_3[idx+len(country)+6:].strip()
                            break
                    

                        if not address: 
                            # check: if there is something after country name
                            if ',' in text_3[idx+len(country):idx+len(country)+10]:
                                continue

                            elif '.' in text_3[idx+len(country):idx+len(country)+10] or '#' in text_3[idx+len(country):idx+len(country)+10]:
                                print('Warning: cannot find the end of address!')
                                break
                            
                            elif checked_text_3.isupper():
                                continue
                    
                            
                            else:
                                # assume no post code
                                address = text_3[:idx+len(country)].strip()
                                text_3 = text_3[idx+len(country):].strip()
                                print(f'address:{address}')
                                print(f'text_3:{text_3}')
                                break
                            
            if address:
                match = re.search('\d', address)
                if match:
                    idx = match.start()
                    if len(address)-idx >30:
                        name = name + address[:idx]
                        address = address[idx:]
                else:
                    match = re.search('\d', text_3)
                    if match:
                        idx = match.start()
                        if idx <20:
                            name = name + text_3[:idx]
                            text_3 = text_3[idx:]
                    # default address
                    # assume ID No begin with letter, while address end with at least 4 digits
                    pattern = r"(\d{4}[A-Z]+\d{2})"
                    match = re.search(pattern, text_3)
                    if match:
                        address = text_3[:match.start()+4]
                        text_3 = text_3[match.start()+4:]
                        check_entry = [address, '']
                # cannot find country name
                if not country:
                
                    print(f'Cannot find country in the address: {text_3[:30]}')
                    
            else:
                print(f'Cannot find name in {pdf_index}th pdf!')
                print(text_3[:20])
                flag = 1


        # No.
        if address and len(text_3) > 5:
            len_no = min(30, len(text_3))
            
            for i in range(len_no):
                # loose: as long as the next term is upper + lower
                if text_3[i+1:i+4] in ['NRI', 'FIN', 'ACR']:
                    No = text_3[:i+1].strip()
                    text_3 = text_3[i+1:].strip()
                    print(f'\n first No: {No}\n')
                    break

        else:
            print(f'Cannot find address in {pdf_index}th pdf!')
            print(text_3[:20])
            flag = 1 

    

        # ID Type  
        if No and len(text_3) > 5:
            index = text_3[:6].find('IN')
            if index != -1:
                ID_type = 'FIN'
                if index != 1:
                    No = No + text_3[:index]
                    text_3 = 'F' + text_3
                text_3 = text_3[index+3:].strip()
            else:
                index = text_3[:20].find('RIC')
                if index != -1:
                    print('Find "NRIC"!')
                    # check if first letter was included in No
                    # if index == 0: 
                    #     No = No[:-1] 
                    if index != 1:
                        print('first letter was included in No')
                        No = No + text_3[:index]
                        text_3 = 'N' + text_3
                    if 'Citiz' in text_3[index+4: 20]:
                        print('Find "Citiz"!')
                        inx = text_3[:20].find('en')
                        if inx != -1:
                            print('Find "en"!')
                            ID_type = text_3[:inx+2].strip()
                            print(f'ID_type:{ID_type}')
                            text_3 = re.sub(ID_type, '', text_3, count = 1).strip()
                    elif 'Perma' in text_3[: 30]:
                        print('Find "Perma"!')
                        # ID_type = 'NRIC Permanent Resident'
                        inx = text_3[: 30].find('dent')
                        if inx != -1:
                            print('Find "dent"!')
                            ID_type = text_3[:inx+4]
                            print(f'ID_type:{ID_type}')
                            text_3 = re.sub(ID_type, '', text_3, count = 1).strip()
                else:
                    index = text_3[:20].find('CRA')
                    print('Find "ACRA"!')
                    if index != -1:
                        if index != 1:
                            No = No + text_3[:index]
                            text_3 = 'A' + text_3
                        if 'Regis' in text_3[: 30]:
                            # ID_type = 'ACRA Registration Number'
                            inx = text_3[:30].find('er')
                            if inx != -1:
                                print('Find "er"!')
                                ID_type = text_3[:inx+2]
                                print(f'ID_type:{ID_type}')
                                text_3 = re.sub(ID_type, '', text_3, count = 1).strip()
                print(f'ID Type: {ID_type}')

                
        else:
            print(f'Cannot find No. in {pdf_index}th pdf!')
            print(text_3[:30])
            flag = 1

        # Country
        if ID_type and len(text_3) > 5:
            while text_3[:3] == ID_type[:3]:
                print('Repeated ID_Type!')
                text_3 = re.sub(ID_type,'', text_3, count=1).strip()
                print(f'Delete the repeatecd ID_Type: {text_3[:30]}')
            matches = list(re.finditer(r'\d', ID_type[:30]))
            if matches:
                last_digit_index = matches[-1].end()
                No = No + ID_type[:last_digit_index+1]
                ID_type = ID_type[last_digit_index+1:]
                print('Tip: check the ID No and ID Type!')
            len_ctry = min(20, len(text_3))
            for i in range(len_ctry):
                if text_3[i-2:i+1].isupper() and text_3[i+1] == ' ' and text_3[i+2].isupper() and text_3[i+3:i+7].islower():
                    ctry = text_3[:i+1].strip(
                    )
                    print(f'country: {ctry}')
                    text_3 = text_3[i+1:].strip()
                    break
                elif text_3[i-2:i+1].isupper() and text_3[i+1].isupper() and text_3[i+2:i+6].islower():
                    ctry = text_3[:i+1].strip(
                    )
                    print(f'country: {ctry}')
                    text_3 = text_3[i+1:].strip()
                    break

        else:
            print(f'Cannot find ID Type in {pdf_index}th pdf!')
            print(text_3[:20])
            flag = 1

        # Position
        if ctry and len(text_3) > 5:
            len_pos = min(60, len(text_3))
            for i in range(len_pos):
                if text_3[i].islower() and text_3[i+1] == ' ' and text_3[i+2].isdigit():
                    pos = text_3[:i+1].strip()
                    # print(f'Position: {pos}')
                    text_3 = text_3[i+1:].strip()
                    break
        else:
            print(f'Cannot find Country in {pdf_index}th pdf!')
            print(text_3[:20])
            flag = 1

        # Appointment date
        if pos and len(text_3) > 5:
            len_appt_date = min(11, len(text_3))
            for i in range(len_appt_date):
                if text_3[0].isdigit() and text_3[3:5].isalpha() and text_3[i-3:i+1].isdigit():
                    appt_date = text_3[:i+1].strip()
                    # print(f'Appointment date: {appt_date}')
                    text_3 = text_3[i+1:].strip()
                    break
        else:
        
            print(f'Cannot find Position in {pdf_index}th pdf!')
            print(text_3[:20])
            flag = 1

        # Discosure date
        if appt_date and len(text_3) > 5:
            len_disc_date = min(11, len(text_3))
            for i in range(len_disc_date):
                if text_3[0].isdigit() and text_3[3:5].isalpha() and text_3[i-3:i+1].isdigit():
                    disc_date = text_3[:i+1].strip()
                    # print(f'Discosure date: {disc_date}')
                    if len(text_3)>i+1:
                        text_3 = text_3[i+1:].strip()
                        remaining_text = text_3
                    else:
                        flag = 1
                    break
        else:
            print(f'Cannot find Appointment date in {pdf_index}th pdf!')
            print(text_3[:20])
            flag = 1

        if not disc_date:
            disc_date = ''
            print(f'Cannot find Disclosure date in {pdf_index}th pdf!')
            print(text_3[:20])
            flag = 1
        
        
        if flag == 1 and text_3[:20].count('-') // 8 > 0:
            name = address = No = ID_type = ctry = pos = appt_date = disc_date = '-'
            if text_3[:20].count('-') // 8 > 1:
                text_3 = re.sub('-', '', text_3, count=9)
                flag = 0
            
        entry = [pdf_index, name, address, No, ID_type, ctry, pos, appt_date, disc_date]


            
        if '' in entry:
            empty_index = entry.index('')
            # entry[empty_index] = text_3
        else:
            empty_index = ''


        print(f'Finish one entry of the {pdf_index}th pdf')
        
        return entry, flag, remaining_text, empty_index, check_entry
    

    def foreign_curr_appt(self, origin_text_3, pdf_index, file_list, txt_dir):
        check_addr_list = []
        flag = 0 # 0: have remaining text -> continue extracting
        remaining_text = ''
        name = address = No = ID_type = ctry = pos = appt_date = disc_date = ''
        check_entry = []

        # locate ID Type first
        p_index = origin_text_3[:200].find('Passport')
        if p_index != -1:
            print('\nFound PASSPORT ID TYPE!\n')
            text_3_1 = origin_text_3[:p_index] # before ID type
            text_3_2 = origin_text_3[p_index:]
            # other type like FIN may also appear, in case involve them in the No.
            idx = text_3_1.find("FIN ")
            if idx != -1:
                text_3_1 = origin_text_3[:idx]
                text_3_2 = origin_text_3[idx:]
                ID_type = 'FIN '

            
            # name: to be safe, always check the name
            text_3_1 = text_3_1.strip()
            if len(text_3_1)>5:
                file_name = file_list[pdf_index]
                txt_path, lines = self.get_txt_lines(txt_dir, file_name)
                text_3_1 = text_3_1.strip()
                name_kwd = text_3_1.split()[0]
                print(f'name_kwd:{name_kwd}')
                if name_kwd != '-':
                    confirm_wd_1 = text_3_1.split()[1].strip()
                    print(f'confirm_wd_1:{confirm_wd_1}')
                    confirm_wd_2 = text_3_1.split()[2].strip()
                    print(f'confirm_wd_2: {confirm_wd_2}')
                    name = self.retrieve_name(lines, name_kwd, confirm_wd_1, confirm_wd_2)
                    print(f'retrived name: {name}')
                    conde_name = name.replace('(', ' ').replace(')', ' ')
                    conde_name = re.sub('\s+', ' ', conde_name)
                    print(f'condemned name:{conde_name}')
                    index = text_3_1.find(conde_name)
                    
                    
                    if index != -1:
                        text_3_1= text_3_1[index+len(conde_name):].strip()
                        print(f'text_3_1:{text_3_1}')
                else:
                    flag = 1


            
            # address: loose condition 
            # ! cannot only rely on the results after extracing No, as there maybe empty spaces so cause inaccurate No extraction
            # strategy: set everything behind name as address, then reomve the No part
            if name and len(text_3_1)>5:

                cleaned_text_3_1 = text_3_1.replace(' ', '')
                ctrys = [country for country in countries if country in cleaned_text_3_1] 
                # Q: if we find the country from the cleaned form, how can we locate it in the original text?
                ctrys = [country for country in countries if country in text_3_1] 
                
                idxes = [text_3_1.find(c) + len(c) - 1 for c in ctrys] # end index
                
                
                
                if ctrys:
                    # country = ctrys[-1]
                    country = ctrys[idxes.index(max(idxes))]
                    idx = text_3_1.find(country)
                    print(f'country:{country}')
                    print(f'ctrys:{ctrys}')
                    # confirm its' the right countryb(the actual one may missing)
                    if ',' in text_3_1[idx:]: # e.g.: 53 HOLLAND ROAD #04-07 HOLLAND COLLECTION, THE SINGAPOR
                        print('Seems no country name involved!')
                        check_addr_list.append(text_3_1)
                    print(f'len of text:{len(text_3_1)}, empty space:{idx+len(country)}, digits end{idx+len(country)+7}')
                    
                    if country == 'SINGAPORE' and text_3_1[idx+len(country)] == ' ' and text_3_1[idx+len(country)+1:idx+len(country)+7].isdigit(): 
                        address = text_3_1[:idx+len(country)+7].strip()
                        text_3_1 = text_3_1[idx+len(country)+7:].strip()

                    
                    elif country == 'CHINA' and text_3_1[idx+len(country)] == ' ' and text_3_1[idx+len(country)+1:idx+len(country)+7].isdigit(): 
                        address = text_3_1[:idx+len(country)+7].strip()
                        text_3_1 = text_3_1[idx+len(country)+7:].strip()

                    elif country in [ ' USA','U.S.A.','U.S.A', 'U S A', ' US'] and text_3_1[idx+len(country)] == ' ' and text_3_1[idx+len(country)+1:idx+len(country)+6].isdigit(): 
                        if text_3_1[idx+len(country)+6] == '-':
                            if text_3_1[idx+len(country)+7:idx+len(country)+11].isdigit():
                                address = text_3_1[:idx+len(country)+11].strip()
                                text_3_1 = text_3_1[idx+len(country)+11:].strip()
                        else:
                            address = text_3_1[:idx+len(country)+6].strip()
                            text_3_1 = text_3_1[idx+len(country)+6:].strip()


                    elif country in ['AUSTRALIA', ' AUST'] and text_3_1[idx+len(country)] == ' ' and text_3_1[idx+len(country)+1:idx+len(country)+5].isdigit(): 
                        address = text_3_1[:idx+len(country)+5].strip()
                        text_3_1 = text_3_1[idx+len(country)+5:].strip()

                    elif country == 'SOUTH AFRICA' and text_3_1[idx+len(country)] == ' ' and text_3_1[idx+len(country)+1:idx+len(country)+5].isdigit(): 
                        address = text_3_1[:idx+len(country)+5].strip()
                        text_3_1 = text_3_1[idx+len(country)+5:].strip()

                    elif country in ['JANPAN', ' JPN'] and text_3_1[idx+len(country)] == ' ' and text_3_1[idx+len(country)+1:idx+len(country)+4].isdigit() and text_3_1[idx+len(country)+4] =='-' and text_3_1[idx+len(country)+5:idx+len(country)+9].isdigit(): 
                        address = text_3_1[:idx+len(country)+7].strip()
                        text_3_1 = text_3_1[idx+len(country)+7:].strip()

                    elif country[:6] == 'TAIWAN' and text_3_1[idx+len(country)] == ' ' and text_3_1[idx+len(country)+1:idx+len(country)+7].isdigit(): 
                        address = text_3_1[:idx+len(country)+7].strip()
                        text_3_1 = text_3_1[idx+len(country)+7:].strip()
                        
                    elif country == ' IL ' and text_3_1[idx+len(country):idx+len(country)+5].isdigit():
                            address = text_3_1[:idx+len(country)+5].strip()
                            text_3_1 = text_3_1[idx+len(country)+5:].strip()
                    
                    elif country == 'THAILAND' and text_3_1[idx+len(country)] == ' ' and text_3_1[idx+len(country)+1:idx+len(country)+6].isdigit():
                        address = text_3_1[:idx+len(country)+6].strip()
                        text_3_1 = text_3_1[idx+len(country)+6:].strip()

                    elif country in ["M'SIA", "MALAYSIA"] and text_3_1[idx+len(country)] == ' ' and text_3_1[idx+len(country)+1:idx+len(country)+6].isdigit():
                        address = text_3_1[:idx+len(country)+6].strip()
                        text_3_1 = text_3_1[idx+len(country)+6:].strip()
                    
                    else:
                        if text_3_1[idx+len(country)] and  text_3_1[idx+len(country)]== ' ':
                            print('Need further identity end of address!')
                        else:
                            # by default: remove anything after country name
                            address = text_3_1[:idx+len(country)].strip()
                            text_3_1 = text_3_1[idx+len(country):].strip()
                if not address:
                    # default address
                    print('Warning: Cannot find country/city name in address!')
                    # check_addr_list.append(text_3_1)
                    # check if involving name
                    match = re.search('\d', text_3_1)
                    if match:
                        idx = match.start()
                        if idx <20:
                            name = name + text_3_1[:idx]
                            text_3_1 = text_3_1[idx:]
                    # default address
                    # assume ID No begin with letter, while address end with at least 4 digits
                    pattern = r"(\d{4}[A-Z]+\d{2})"
                    match = re.search(pattern, text_3_1)
                    if match:
                        address = text_3_1[:match.start()+4]
                        text_3_1 = text_3_1[match.start()+4:]
                        check_entry = [address, '']


                else:
                    match = re.search('\d', address)
                    if match:
                        idx = match.start()
                        if len(address)-idx >30:
                            name = name + address[:idx]
                            address = address[idx:]
                    print(f'address:{address}')

            else:
                print(f'Cannot find name in {pdf_index}th pdf!')
                print(text_3_1[:20])
                flag = 1

            # No
            # by default: 9 numbers
            # assumption: should not include all alphat part of address
            if address:
                No = text_3_1
                cleaned_text_3_1 = re.sub(r'[^A-Za-z0-9]', '', text_3_1)
                # todo: decide the length of each No to segament the string modulo     
                No_1 = No_2 = No_3 = ''
                # cannot be divided by 9
                if cleaned_text_3_1:
                    n = len(cleaned_text_3_1)
                    if n % 9 == 0:
                        No_3 = cleaned_text_3_1[-9:]
                        cleaned_text_3_1 = cleaned_text_3_1[:-9]
                        if len(cleaned_text_3_1)>8:
                            No_2 = cleaned_text_3_1[-9:]
                            cleaned_text_3_1 = cleaned_text_3_1[:-9]
                            if len(cleaned_text_3_1)>8:
                                No_1 = cleaned_text_3_1[-9:]
                                cleaned_text_3_1 = cleaned_text_3_1[:-9].strip()
                        
                    elif n % 9 == 8:
                        if n<9:
                            No_1 = cleaned_text_3_1
                        else:
                            No_1 = cleaned_text_3_1[:9]
                            cleaned_text_3_1 = cleaned_text_3_1[9:]
                            if len(cleaned_text_3_1)>8:
                                No_2 = cleaned_text_3_1[:9]
                                No_3 = cleaned_text_3_1[9:]
                            else:
                                No_2 = cleaned_text_3_1
                    
                    elif n % 9 == 7:
                        if n < 9:
                            print('Warning: No at length 7!')
                        else:  
                            if len(cleaned_text_3_1)>18:
                                No_1 = cleaned_text_3_1[:9]
                                cleaned_text_3_1 = cleaned_text_3_1[9:]
                                No_2 = cleaned_text_3_1[:8]
                                No_3 = cleaned_text_3_1[8:]
                            else:
                                No_1 = cleaned_text_3_1[:8]
                                No_2 = cleaned_text_3_1[8:]
                    
                    elif n % 9 <3 and n>9:
                        No = cleaned_text_3_1 # partition
                        # need improvement

                    elif n > 10:
                        # error in address extraction
                        x = n % 9
                        address = address + cleaned_text_3_1[:x]
                        cleaned_text_3_1 = cleaned_text_3_1[x:]
                        n = n-x
                        No_3 = cleaned_text_3_1[-9:]
                        cleaned_text_3_1 = cleaned_text_3_1[:-9]
                        if len(cleaned_text_3_1)>8:
                            No_2 = cleaned_text_3_1[-9:]
                            cleaned_text_3_1 = cleaned_text_3_1[:-9]
                            if len(cleaned_text_3_1)>8:
                                No_1 = cleaned_text_3_1[-9:]
                    
                    else:
                        print('Error in extracting No!')
                        print(f'cleaned_text_3_1: {cleaned_text_3_1}')
                        flag = 1

                    if No_1 or No_2 or No_3:
                        No = No_1 + ' ' +  No_2 + ' ' + No_3
                        No = No.strip()
                    

                print(f'No:{No}')
            
            else:
                print('Cannot find address!')
                flag = 1
            

            # ID_type and afterwards
            index = text_3_2[:20].find('ers')
            if index != -1:
                ID_type = text_3_2[:index + 3].strip()
                text_3_2 = text_3_2[index + 3:].strip()
                print(f'ID Type: {ID_type}')
            else:
                print(f'Cannot find ID_type in {pdf_index}th pdf!')
                print(text_3_2[:20])
                flag = 1

            # Country
            if ID_type and len(text_3_2) > 5:
                # check and deal with repeated ID_type
                while text_3_2[:3] == ID_type[:3]:
                    print(f'Find repeated ID_Type:{ID_type} of {text_3_2[:20]}')
                    text_3_2 = re.sub(ID_type,'', text_3_2, count=1).strip()
                matches = list(re.finditer(r'\d', ID_type[:30]))
                if matches:
                    last_digit_index = matches[-1].end()
                    No = No + ID_type[:last_digit_index+1]
                    ID_type = ID_type[last_digit_index+1:]
                    print('Tip: check the ID No and ID Type!')
                len_ctry = min(20, len(text_3_2))
                for i in range(len_ctry):
                    if text_3_2[i-2:i+1].isupper() and text_3_2[i+1] == ' ' and text_3_2[i+2].isupper() and text_3_2[i+3:i+7].islower():
                        ctry = text_3_2[:i+1].strip(
                        )
                        print(f'country: {ctry}')
                        text_3_2 = text_3_2[i+1:].strip()
                        break
                    elif text_3_2[i-2:i+1].isupper() and text_3_2[i+1].isupper() and text_3_2[i+2:i+6].islower():
                        ctry = text_3_2[:i+1].strip(
                        )
                        print(f'country: {ctry}')
                        text_3_2 = text_3_2[i+1:].strip()
                        break


            # Position
            if ctry and len(text_3_2) > 5:
                len_pos = min(60, len(text_3_2))
                for i in range(len_pos):
                    if text_3_2[i].islower() and text_3_2[i+1] == ' ' and text_3_2[i+2].isdigit():
                        pos = text_3_2[:i+1].strip()
                        # print(f'Position: {pos}')
                        text_3_2 = text_3_2[i+1:].strip()
                        break
            else:
                print(f'Cannot find Country in {pdf_index}th pdf!')
                print(text_3_2[:20])
                flag = 1

            # Appointment data
            if pos and len(text_3_2) > 5:
                len_appt_date = min(11, len(text_3_2))
                for i in range(len_appt_date):
                    if text_3_2[0].isdigit() and text_3_2[3:5].isalpha() and text_3_2[i-3:i+1].isdigit():
                        appt_date = text_3_2[:i+1].strip()
                        # print(f'Appointment date: {appt_date}')
                        text_3_2 = text_3_2[i+1:].strip()
                        break
            else:
                print(f'Cannot find Position in {pdf_index}th pdf!')
                print(text_3_2[:20])
                flag = 1

            # Discosure date
            if appt_date and len(text_3_2) > 5:
                len_disc_date = min(11, len(text_3_2))
                for i in range(len_disc_date):
                    if text_3_2[0].isdigit() and text_3_2[3:5].isalpha() and text_3_2[i-3:i+1].isdigit():
                        disc_date = text_3_2[:i+1].strip()
                        # print(f'Discosure date: {disc_date}')
                        if len(text_3_2)>i+1:
                            text_3_2 = text_3_2[i+1:].strip()
                            remaining_text = text_3_2
                        else:
                            print('No remaining text!')
                            flag = 1
                        break
            else:
                print(f'Cannot find Appointment date in {pdf_index}th pdf!')
                print(text_3_2[:20])
                flag = 1

            if not disc_date:
                disc_date = ''
                print(f'Cannot find Disclosure date in {pdf_index}th pdf!')
                print(text_3_2[:20])
                flag = 1
        else:
            print('Cannot find Passport ID Type!')
            text_3_1 = origin_text_3
            text_3_2 = ''
        
        entry = [pdf_index, name, address, No, ID_type, ctry, pos, appt_date, disc_date]


        
        if '' in [pdf_index, name, address, No]:
            empty_index =[pdf_index, name, address, No].index('')
            # entry[empty_index] = text_3_1 + ' ' + text_3_2

        elif '' in [ID_type, ctry, pos, appt_date, disc_date]:
            empty_index =[ID_type, ctry, pos, appt_date, disc_date].index('')
            # entry[empty_index] = text_3_2
        else:
            empty_index = ''

        print(f'Finish one foreign entry of the {pdf_index}th pdf')

        return entry, flag, remaining_text, empty_index, check_entry


    def extract_curr_appt_holder(self, exl_path, missing_exl_path, check_exl_path, text_list, file_list, txt_dir):
        curr_appt_holder_df = pd.DataFrame(columns = ['pdf index', 'Name', 'Address', 'No.', 'ID type', 'Country', 'Position', 'Appointment data', 'Discosure date'])
        curr_appt_holder_missing = pd.DataFrame(columns=['pdf index', 'file name', 'line index', 'column index', 'remaining_text'])
        check_appt_holder_df = pd.DataFrame(columns = ['pdf_index', 'file name', 'row index', 'obtained address','obtained ID No'])

        # remaining issue about address: 
        # 1. for those address without digits, hard to tell them apart.
        # 2. for those start with alpha + digits, may msitakenly include alphas into the name, or lead to failure in extraction of the whole entry

        # solution: select from the original text

        for i in range(len(text_list[3])):
            text_3 = text_list[3][i]
            pdf_name = file_list[i]
            # remove token when crosses pages
            token_1 = r'(ENTITY\s*PROFILE\s*REPORT\s*.*\s*\d{1,2}\s*\w+\s*\d{4}\s*\|\s*\d{1,2}:\d{2}\s*[ap]m\s*Created\s*by:\s*chantw1\s*Private\s*&\s*Confidential\s*Page\s*\d+\s*of\s*\d+\s*)'
            token_2 = r'((.*\s*\d{1,2}\s*\w+\s*\d{4}\s*)?\|\s*\d{1,2}:\d{2}\s*[ap]m\s*Created\s*by:\s*chantw1\s*Private\s*&\s*Confidential\s*Page\s*\d+\s*of\s*\d+\s*)'
            text_3 = re.sub(token_1, ' ', text_3).strip()
            text_3  = re.sub(token_2, ' ', text_3 ).strip()

            token_1 = r'(ENTITY\s*PROFILE\s*REPORT\s*.*\s*\d{1,2}\s*\w+\s*\d{4}\s*\|\s*\d{1,2}:\d{2}\s*[ap]m\s*Created\s*by:\s*oiada\s*Private\s*&\s*Confidential\s*Page\s*\d+\s*of\s*\d+\s*)'
            # Case 2: No entity profile report 
            token_2 = r'((.*\s*\d{1,2}\s*\w+\s*\d{4}\s*)?\|\s*\d{1,2}:\d{2}\s*[ap]m\s*Created\s*by:\s*oiada\s*Private\s*&\s*Confidential\s*Page\s*\d+\s*of\s*\d+\s*)'
            text_3 = re.sub(token_1, '', text_3).strip()
            text_3  = re.sub(token_2, '', text_3 ).strip()
            text_3  = re.sub(r'[()\[\]{}]', ' ', text_3 )
            text_3  = re.sub(r'\n', ' ', text_3)
            text_3 = re.sub(r'\.', ' ', text_3)
            text_3  = re.sub(r'\s+', ' ', text_3)
            text_3 = re.sub(r'/', '', text_3)
            
            # print(text_3)
            pattern = r'Disclosure Date\s*(.*)'

            # Search for the pattern
            match = re.search(pattern, text_3)

            # Check if a match was found
            if match:
                # Extract the string after 'Disclosure Date'
                text_3 = match.group(1)
                if match.group(0).strip() == 'Disclosure Date':
                    flag = 1
                    entry = [i] + ['-']*8
                    curr_appt_holder_df = pd.concat([curr_appt_holder_df, pd.DataFrame([entry], columns=curr_appt_holder_df.columns)], ignore_index= True)
                    continue
                
                flag = 0
                line = 0
                while flag ==0:
                    original_text_3 = text_3
                    entry, flag, remaining_text, missing_index, check_entry = self.entry_curr_appt(text_3, i, file_list, txt_dir)
                    # check ID No
                    if entry[3]!='' and entry[3]!='-':
                        entry = self.check_no(3, entry)
                    curr_appt_holder_df = pd.concat([curr_appt_holder_df, pd.DataFrame([entry], columns=curr_appt_holder_df.columns)], ignore_index= True)
                    if check_entry:
                        check_entry = [i, pdf_name, line] + check_entry
                        print(f'check_entry:{check_entry}')
                        check_appt_holder_df = pd.concat([check_appt_holder_df, pd.DataFrame([check_entry], columns=check_appt_holder_df.columns)], ignore_index= True)

                    if '' in entry:
                        print('\nPerform foreign check, for passport ID Type\n') 
                        entry_1, flag_1, remaining_text_1, missing_index_1, check_entry_1 = self.foreign_curr_appt(text_3, i, file_list, txt_dir)
                        # check ID No
                        if entry_1[3]!='' and entry_1[3]!='-':
                            entry_1 = self.check_no(3, entry_1)
                        if entry_1[4]!='':
                            entry = entry_1
                            curr_appt_holder_df.iloc[-1] = entry
                            missing_index = missing_index_1
                            remaining_text = remaining_text_1
                            flag = flag_1
                            if check_entry_1:
                                check_entry_1 = [i, pdf_name, line] + check_entry_1
                                print(f'check_entry_1:{check_entry_1}')
                                if check_entry:
                                    check_appt_holder_df.iloc[-1] = check_entry_1
                                else:
                                    check_appt_holder_df = pd.concat([check_appt_holder_df, pd.DataFrame([check_entry_1], columns=check_appt_holder_df.columns)], ignore_index= True)
                        # curr_appt_holder_df.iloc[-1] = entry
                        if len(remaining_text) < 5:
                            flag = 1
                        # update missing_index 
                        # Q: to better loop, maybe it's best to make each info search a function?
                        if '' in entry: # have missing values after filling 
                            missing_index = entry.index('')
                            curr_appt_holder_missing = pd.concat([curr_appt_holder_missing , pd.DataFrame([[i, pdf_name, line, missing_index, " ".join(str(item) for item in entry[1:])]], columns=curr_appt_holder_missing.columns)], ignore_index= True)
                            print('There is still missing values')
                            print(f'original_text_3:{original_text_3}')
                            remaining_text, ending_str = self.locate_end_of_line(2, original_text_3)
                            if len(remaining_text) > 20:
                                flag = 0
                                print(f'remaining_text:{remaining_text}')
                                print(f'ending_str:{ending_str}')
                                
                    
                    text_3 = remaining_text
                    print(f'Continue. text_3:\n {text_3}\n')
                    line += 1
                    
            else:
                print(f'Wrong heading of CURRENT APPOINTMENT HOLDERS of the {i}th pdf!')

        curr_appt_holder_df.to_excel(exl_path, index=False, engine='openpyxl')
        curr_appt_holder_missing.to_excel(missing_exl_path, index=False, engine='openpyxl')
        check_appt_holder_df.to_excel(check_exl_path, index=False, engine='openpyxl')
        print('Finish extracting the current appointment holder!')

    def extract_name(self, text, file_name, txt_dir):
        name = ''
        if len(text)>5:
            txt_path, lines = self.get_txt_lines(txt_dir, file_name)
            text = text.strip()
            name_kwd = text.split()[0]
            print(f'name_kwd:{name_kwd}')
            if name_kwd != '-':
                confirm_wd_1 = text.split()[1].strip()
                print(f'confirm_wd_1:{confirm_wd_1}')
                confirm_wd_2 = text.split()[2].strip()
                print(f'confirm_wd_2: {confirm_wd_2}')
                name = self.retrieve_name(lines, name_kwd, confirm_wd_1, confirm_wd_2)
                print(f'retrived name: {name}')
                conde_name = name.replace('(', ' ').replace(')', ' ')
                conde_name = re.sub('\s+', ' ', conde_name)
                print(f'condemned name:{conde_name}')
                index = text.find(conde_name)
                
                
                if index != -1:
                    text= text[index+len(conde_name):].strip()
                    print(f'text_4:{text}')
            else:
                flag = 1
            return name, text, flag
        

    def extract_address(self, text):
        address = ''
        len_addr = min(150, len(text)-5)
        country = ''
        for i in range(len_addr):
            # method 1: perform country check first on length i (if not have the address by default?)
            s = text[:i+1]
            ctry = [country for country in self.countries if country in s]
            # ctrys = [country for country in s if country in countries]
            if ctry:
                country = ctry[-1]
                print(f'new country in address, potential country of address: {country}')

                # first country name is SG: assume this is SG address -> check 6 digits end (seems repeated)
                if country == 'SINGAPORE':
                    idxes = [match.start() for match in re.finditer(country,s)]
                    for idx in idxes:
                        if len(s) >= idx+16 and s[idx+len(country)]==' ' and s[idx+len(country)+1:idx+len(country)+7].isdigit():
                            print('Confirmed: Singapore address with 6 digits end!')
                            address = s[:idx+16].strip()
                            text = text[idx+16:].strip()
                            break
                    if address:
                        break
                            
                # first country name not SG: 1) Singapore addr(excluded); 2)foreign addr
                else:
                    idx = s.find(country)
                    related_countries = [item for item in self.countries if country in item]
                    idxes = [text[:i+10].find(c) + len(c) - 1 for c in related_countries]
                    country = related_countries[idxes.index(max(idxes))]
                    idx = text.find(country)
                    checked_text = text[i+1:i+5].replace(' ', '')


                    if country == 'CHINA' and text[idx+len(country)] == ' ' and text[idx+len(country)+1:idx+len(country)+7].isdigit(): 
                        address = text[:idx+len(country)+7].strip()
                        text = text[idx+len(country)+7:].strip()
                        break

                    elif country in [ ' USA','U.S.A.','U.S.A', 'U S A', ' US'] and text[idx+len(country)] == ' ' and text[idx+len(country)+1:idx+len(country)+6].isdigit(): 
                        if text[idx+len(country)+6] == '-':
                            if text[idx+len(country)+7:idx+len(country)+11].isdigit():
                                address = text[:idx+len(country)+11].strip()
                                text = text[idx+len(country)+11:].strip()
                                break
                        else:
                            address = text[:idx+len(country)+6].strip()
                            text = text[idx+len(country)+6:].strip()
                            break

                    elif country in ['AUSTRALIA', ' AUST'] and text[idx+len(country)] == ' ' and text[idx+len(country)+1:idx+len(country)+5].isdigit(): 
                        address = text[:idx+len(country)+5].strip()
                        text = text[idx+len(country)+5:].strip()
                        break

                    elif country == 'SOUTH AFRICA' and text[idx+len(country)] == ' ' and text[idx+len(country)+1:idx+len(country)+5].isdigit(): 
                        address = text[:idx+len(country)+5].strip()
                        text = text[idx+len(country)+5:].strip()
                        break

                    elif country in ['JANPAN', ' JPN'] and text[idx+len(country)] == ' ' and text[idx+len(country)+1:idx+len(country)+4].isdigit() and text[idx+len(country)+4] =='-' and text_4[idx+len(country)+5:idx+len(country)+9].isdigit(): 
                        address = text[:idx+len(country)+7].strip()
                        text = text[idx+len(country)+7:].strip()
                        break

                    elif country[:6] == 'TAIWAN' and text[idx+len(country)] == ' ' and text[idx+len(country)+1:idx+len(country)+7].isdigit(): 
                        address = text[:idx+len(country)+7].strip()
                        text = text[idx+len(country)+7:].strip()
                        break
                        
                    elif country == ' IL ' and text[idx+len(country):idx+len(country)+5].isdigit():
                        address = text[:idx+len(country)+5].strip()
                        text = text[idx+len(country)+5:].strip()
                        break
                    
                    elif country == 'THAILAND' and text[idx+len(country)] == ' ' and text[idx+len(country)+1:idx+len(country)+6].isdigit():
                        address = text[:idx+len(country)+6].strip()
                        text = text[idx+len(country)+6:].strip()
                        break

                    elif country in ["M'SIA", "MALAYSIA"] and text[idx+len(country)] == ' ' and text[idx+len(country)+1:idx+len(country)+6].isdigit():
                        address = text[:idx+len(country)+6].strip()
                        text = text[idx+len(country)+6:].strip()
                        break
                

                    if not address: 
                        # check: if there is something after country name
                        if ',' in text[idx+len(country):idx+len(country)+10]:
                            continue

                        elif '.' in text[idx+len(country):idx+len(country)+10] or '#' in text[idx+len(country):idx+len(country)+10]:
                            print('Warning: cannot find the end of address!')
                            break
                        
                        elif checked_text.isupper():
                            continue
                
                        
                        else:
                            # assume no post code
                            address = text[:idx+len(country)].strip()
                            text = text[idx+len(country):].strip()
                            print(f'address:{address}')
                            print(f'text:{text}')
                            break

        if address:
            match = re.search('\d', address)
            if match:
                idx = match.start()
                if len(address)-idx >30:
                    name = name + address[:idx]
                    address = address[idx:]
            else:
                match = re.search('\d', text)
                if match:
                    idx = match.start()
                    if idx <20:
                        name = name + text[:idx]
                        text = text[idx:]
                # default address
                # assume ID No begin with letter, while address end with at least 4 digits
                pattern = r"(\d{4}[A-Z]+\d{2})"
                match = re.search(pattern, text)
                if match:
                    address = text[:match.start()+4]
                    text = text[match.start()+4:]
                    check_entry = [address, '']
            # cannot find country name
            if not country:
            
                print(f'Cannot find country in the address: {text[:30]}')
                
        return address, text
    

    def extract_ID_type(self, text):
        ID_type = ''
        index = text[:6].find('IN')
        if index != -1:
            ID_type = 'FIN'
            if index != 1:
                No = No + text[:index]
                text = 'F' + text
            text = text[index+3:].strip()
        else:
            index = text[:20].find('RIC')
            if index != -1:
                print('Find "NRIC"!')
                # check if first letter was included in No
                # if index == 0: 
                #     No = No[:-1] 
                if index != 1:
                    print('first letter was included in No')
                    No = No + text[:index]
                    text = 'N' + text
                if 'Citiz' in text[index+4: 20]:
                    print('Find "Citiz"!')
                    inx = text[:20].find('en')
                    if inx != -1:
                        print('Find "en"!')
                        ID_type = text[:inx+2].strip()
                        print(f'ID_type:{ID_type}')
                        text = re.sub(ID_type, '', text, count = 1).strip()
                elif 'Perma' in text[: 30]:
                    print('Find "Perma"!')
                    # ID_type = 'NRIC Permanent Resident'
                    inx = text[: 30].find('dent')
                    if inx != -1:
                        print('Find "dent"!')
                        ID_type = text[:inx+4]
                        print(f'ID_type:{ID_type}')
                        text = re.sub(ID_type, '', text, count = 1).strip()
            else:
                index = text[:20].find('CRA')
                print('Find "ACRA"!')
                if index != -1:
                    if index != 1:
                        No = No + text[:index]
                        text = 'A' + text
                    if 'Regis' in text[: 30]:
                        # ID_type = 'ACRA Registration Number'
                        inx = text[:30].find('er')
                        if inx != -1:
                            print('Find "er"!')
                            ID_type = text[:inx+2]
                            print(f'ID_type:{ID_type}')
                            text = re.sub(ID_type, '', text, count = 1).strip()
            print(f'ID Type: {ID_type}')   
        return ID_type, text
    

    def extract_ctry(self, text):
        start_time = time.time()
        while text[:3] == ID_type[:3]:
            print('Repeated ID_Type!')
            text = re.sub(ID_type,'', text, count=1).strip()
            print(f'Delete the repeatecd ID_Type: {text[:30]}')
            elapsed_time = time.time() - start_time
            if elapsed_time > 30:
                print('Too long time in deleting repeated ID Type!')
                break
        matches = list(re.finditer(r'\d', ID_type[:30]))
        if matches:
            last_digit_index = matches[-1].end()
            No = No + ID_type[:last_digit_index+1]
            ID_type = ID_type[last_digit_index+1:]
            print('Tip: check the ID No and ID Type!')
        len_ctry = min(20, len(text))
        for i in range(len_ctry):
            if text[i-2:i+1].isupper() and text[i+1] == ' ' and text[i+2].isupper() and text[i+3:i+7].islower():
                ctry = text[:i+1].strip(
                )
                print(f'country: {ctry}')
                text = text[i+1:].strip()
                break
            elif text[i-2:i+1].isupper() and text[i+1].isupper() and text[i+2:i+6].islower():
                ctry = text[:i+1].strip(
                )
                print(f'country: {ctry}')
                text = text[i+1:].strip()
                break
        return ctry, text
    

    def extract_share_type(self, text):
        len_share_type = min(30, len(text))
        for i in range(len_share_type):
            if text[0].isupper() and text[1].islower() and text[i].islower() and text[i+1] == ' ' and text[i+2:i+4].isupper():
                share_type = text[:i+1].strip()
                print(f'share type: {share_type}')
                # print('there is a space')
                text= text[i+1:].strip()
                break
        return share_type, text
        

    def extract_currency(self, text):
        len_currency = min(5, len(text))
        for i in range(len_currency):
            if text[:i+1].isupper() and text[i+1].isdigit():
                currency = text[:i+1].strip()
                print(f'currency: {currency}')
                text = text[i+1:].strip()
                break
        return currency, text
    
    def extract_num_of_shares(self, text):
        len_num_shares = min(15, len(text))
        for i in range(len_num_shares):
            if text[i].isdigit() and text[i+1] == ' ' and text[i+2].isdigit():
                num_shares = text[:i+1].strip()
                print(f'number of shares: {num_shares}')
                text = text[i+1:].strip()
                break
        return num_shares, text
    

    def extract_disc_date(self, text):
        len_disc_date = min(11, len(text))
        for i in range(len_disc_date):
            if text[0].isdigit() and text[3:5].isalpha() and text[i-3:i+1].isdigit():
                disc_date = text[:i+1].strip()
                # print(f'Discosure date: {disc_date}')
                if len(text)>i+1:
                    text = text[i+1:].strip()
                    remaining_text = text
                else:
                    flag = 1
                break
        return disc_date, text


    def entry_share_appt(self, text_4, pdf_index, file_list, txt_dir):
        flag = 0 # 0: have remaining text -> continue extracting
        remaining_text = ''
        name = address = No = ID_type = ctry = share_type = currency = num_shares = disc_date = ''
        check_entry = []
        file_name = file_list[pdf_index]
        name, text_4, flag = self.extract_name(text_4,file_name, txt_dir)

        # address: 
        # special those without 6 digits end
        # Q: which way is more accurate -- first search for country or not (if not, after using 6 digits need to check)?
        if name and len(text_4) > 5:
            address, text_4 = self.extract_address(text_4)
        else:
            print(f'Cannot find name in {pdf_index}th pdf!')
            print(text_4[:20])
            flag = 1
    

        # ID Type  
        if No and len(text_4) > 5:
            ID_type, text_4 = self.extract_ID_type(text_4)
        else:
            print(f'Cannot find No. in {pdf_index}th pdf!')
            print(text_4[:30])
            flag = 1

        # Country
        if ID_type and len(text_4) > 5:
            ctry, text_4 = self.extract_ctry(text_4)
        else:
            print(f'Cannot find ID Type in {pdf_index}th pdf!')
            print(text_4[:20])
            flag = 1
            

        # share type
        if ctry and len(text_4) > 5:
            share_type, text_4 = self.extract_share_type(text_4)
                # elif text_4[0].isupper() and text_4[1].islower() and text_4[i].islower() and text_4[i+1:i+3].isupper():
                #     share_type = text_4[:i+1].strip()
                #     print(f'share type: {share_type}')
                #     # print('there is no space')
                #     text_4 = text_4[i+1:].strip()
                #     break
        else:
            print(f'Cannot find Country in {pdf_index}th pdf!')
            print(text_4[:20], '\n')
            flag = 1
        
        # currency
        if share_type and len(text_4) > 5:
            currency, text_4 = self.extract_currency(text_4)
        else:
            print(f'Cannot find Share Type in {pdf_index}th pdf!')
            print(text_4[:20])
            flag = 1     


        # number of shares
        if currency and len(text_4) > 5:
            num_shares, text_4 = self.extract_num_of_shares(text_4)
        else:
            print(f'Cannot find Currency in {pdf_index}th pdf!')
            print(text_4[:20])
            flag = 1 
                
        # disclosure date
        if num_shares and len(text_4) > 5:
            disc_date, text_4 = self.extract_disc_date(text_4)

        else:
            print(f'Cannot find Number of Shares in {pdf_index}th pdf!')
            print(text_4[:20])
            flag = 1



        if not disc_date:
            disc_date = ''
            print(f'Cannot find Disclosure date in {pdf_index}th pdf!')
            print(text_4[:20])
            flag = 1
        
        
        if flag == 1 and text_4[:20].count('-') // 9 > 0:
            name = address = No = ID_type = ctry = share_type = currency = num_shares = disc_date = '-'
            if text_4[:20].count('-') // 9 > 1:
                text_4 = re.sub('-', '', text_4, count=9)
                flag = 0
        
        entry = [file_name, name, address, No, ID_type, ctry, share_type, currency, num_shares, disc_date]
        

        if '' in entry:
            empty_index = entry.index('')
            # entry[empty_index] = text_4
        else:
            empty_index = ''

        print(f'Finish one entry of the {pdf_index}th pdf')

        
        return entry, flag, remaining_text, empty_index, check_entry