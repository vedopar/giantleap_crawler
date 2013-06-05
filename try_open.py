'''
Created on May 27, 2013

@author: ved
'''
import spynner,sqlite3
from pyquery import PyQuery
from StringIO import StringIO

url_base="http://www.giantleap.us/progapp/list/"
degrees=["MS","PhD"]
professions=["EE","CpE","ME","AE","ChemE","BME","MSE","EnvE","CivE"]
info_tables=[["deadline_fee","GRE","TOEFL","rl","cost","gtScore"],["deadline_fee","GRE","TOEFL","rl","gtScore"]]
debug_stream = StringIO()

def get_table(prof,page_id):
    url_suffix=""
    is_continue=True
    if page_id>0:
        url_suffix="#.startPage="+str(page_id)
        
    all_data=[[["" for j1 in range(31)] for i1 in range(10)],[["" for j2 in range(26)] for i2 in range(10)]]
    
    
    for deg_i in range(len(degrees)):
        is_name_checked=False
        deg=degrees[deg_i]
        data=all_data[deg_i]
        url_temp_base=url_base+prof+"_"+deg+"/"+prof+","+deg+"/"
        offset=0
        skip=False
        for info in info_tables[deg_i]:
            if skip==True:
                break
            url=url_temp_base+info+".htm"+url_suffix
            browser = spynner.Browser(debug_level=spynner.DEBUG, debug_stream=debug_stream)
            browser.load(url,load_timeout=20)
            d = PyQuery(browser.html)
            #browser.wait_for_content(callback)
            #print browser.html
            rows = d('tr')
            
            row_length=0
            if is_name_checked:
                row_length=rows.eq(0).children().size()-2
            else:
                row_length=rows.eq(0).children().size()+1

            for i in range(rows.size())[1:]:
                tds=rows.eq(i).children()
                if not is_name_checked:
                    data[i-1][0]=tds.eq(0).text()
                    text=tds.eq(1).text()
                    if text=="":
                        is_continue=False
                        skip=True
                        break
                    text=text.split(" ")
                    data[i-1][1]=" ".join(text[2:-2])
                    data[i-1][2]=text[-1]
                    for j in range(tds.size()-2):
                        #print j+3,
                        data[i-1][j+3]=tds.eq(j+2).text()
                else:
                    for j in range(tds.size()-2):
                        text=tds.eq(j+2).text()
                        if text != "" or text != " ":
                            #print offset+j,
                            data[i-1][offset+j]=text
                        else:
                            #print offset+j,
                            data[i-1][offset+j]="None"
            offset=offset+row_length                
            is_name_checked=True
            browser.close()
    return is_continue,all_data
            
def write_to_db(prof,all_data):
    con=sqlite3.connect('testdbT')
    cursor=con.cursor()
    ms_table_name=prof+"_"+degrees[0]
    phd_table_name=prof+"_"+degrees[1]
    cursor.execute('create table if not exists  '+ms_table_name+
                   '(ranking_id text primary key,major_name text,univ_name text,apply_fall text,'+
                   'apply_fellowship text,apply_scholarship text,'+
                   'apply_other text,apply_spring text,apply_fee text,'+
                   'gre_require text,gre_verbal text,gre_quan text,'+
                   'gre_writing text,ibt_require text,ibt_read text,'+
                   'ibt_listen text,ibt_speak text,ibt_write text,'+
                   'ielts text,web_recom text,paper_recom text,'+
                   'recom_table text,tuition_semester text,tuition_year text,'+
                   'tuition_total text,cost_year text,fund_proof text,'+
                   'gre_phone text,toefl_phone text,'+
                   'gre_print text,toefl_print text)')
    cursor.execute('create table if not exists  '+phd_table_name+
                   '(ranking_id text primary key,major_name text,univ_name text,apply_fall text,'+
                   'apply_fellowship text,apply_scholarship text,'+
                   'apply_other text,apply_spring text,apply_fee text,'+
                   'gre_require text,gre_verbal text,gre_quan text,'+
                   'gre_writing text,ibt_require text,ibt_read text,'+
                   'ibt_listen text,ibt_speak text,ibt_write text,'+
                   'ielts text,web_recom text,paper_recom text,'+
                   'recom_table text,gre_phone text,toefl_phone text,'+
                   'gre_print text,toefl_print text)')
    for row in all_data[1]:
        str1=tuple(row)
        cursor.execute("INSERT OR REPLACE INTO "+phd_table_name+" VALUES (?,?,?,?,?,?,?,?,?,?,"+
                       "?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",str1);
    for row2 in all_data[0]:
        str2=tuple(row2)
        cursor.execute("INSERT OR REPLACE INTO "+ms_table_name+" VALUES (?,?,?,?,?,?,?,?,?,?,"+
                       "?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",str2);      
    con.commit()
    cursor.close()
    con.close()

if __name__ == '__main__':
    
    prof_id=0
    while prof_id<len(professions):
        page_id=0
        is_continue=True
        while is_continue:
            try:
                is_continue,data=get_table(professions[prof_id],page_id)
            except spynner.browser.SpynnerTimeout:
                is_continue=True
                continue
            
            print "read data completed page "+str(page_id)
            write_to_db(professions[prof_id],data)
            print "db process end"
            page_id=page_id+1
        print "end prof",prof_id
        prof_id=prof_id+1
    
    
        