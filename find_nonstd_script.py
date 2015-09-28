#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: ZhenjieRuan
# @Date:   2015-09-27 17:10:24
# @Last Modified by:   ZhenjieRuan
# @Last Modified time: 2015-09-27 17:12:33
# @This programme is inteded to search thorugh
# @the parse blockchain file and find nonstandard
# @transactions scripts
import re


#parsed block chain data
raw_dump = open('rawdump.txt','r')
raw_dump = raw_dump.readlines()
#output file of nonstandard transaction scripts
output = open('interesting_scripts.txt','w+')
#types of transaction to exclude
ex_list = ["'pays to hash160(pubkey)\n'","'pays to explicit uncompressed pubKey'\n"]
#current count of bracket encountered,used to retrieve blocks of data when encounter transaction
brack_count = 0


def main():

    for l in range(0,len(raw_dump)):
        #check if the transaction section starts, if true
        #construct a dictionary of the data included
        trans = {}#transaction dictionary
        if "transactions" in raw_dump[l]:
            brack_count = 1
            #trans_dic.update({"transactions":[]})
            while brack_count > 0:
                #read next line
                l += 1
                line = raw_dump[l]
                #cut leading spaces of line
                line = line.lstrip()
                if '{' in line:
                    brack_count += 1
                elif '}' in line:
                    brack_count -= 1
                #check if line is start of a tx block
                if re.match("tx(?=[0-9]+)",line):
                    #brack_count += 1
                    #add this tx to transaction dictionary
                    current_tx = re.split("(?<==)\s|\s(?==)",line)[0]
                    trans.update({current_tx:{}})
                    #read next line
                    l += 1
                    line = raw_dump[l]
                    line = line.lstrip()
                    #find input blocks
                    if "txHash =" in line:
                        #get txHash and get rid of '\n' and '' around the string
                        txHash = re.split("(?<==)\s|\s(?==)",line)[2][:-2][1:]
                        trans[current_tx].update({"txHash":txHash})
                    while not "outputs = {" in line:
                        l += 1
                        line = raw_dump[l]
                        line = line.lstrip()
                        if '{' in line:
                            brack_count += 1
                        elif '}' in line:
                            brack_count -= 1

                        if re.match("input(?=[0-9]+)",line):
                            _input = re.split("(?<==)\s|\s(?==)",line)[0]
                            trans[current_tx].update({_input:"script: "})
                            #skip line of "script = '\n"
                            #first line of this input's script
                            l += 2
                            line = raw_dump[l]
                            line = line.lstrip()
                            #write all the script to its ocrresponding input
                            while not line == "'\n":
                                trans[current_tx][_input]+=line
                                l += 1
                                line = raw_dump[l]
                                line = line.lstrip()
                    #starting of outputs
                    while brack_count > 1:
                        l += 1
                        line = raw_dump[l]
                        line = line.lstrip()
                        if '{' in line:
                            brack_count += 1
                        elif '}' in line:
                            brack_count -= 1

                        if re.match("output(?=[0-9]+)",line):
                            _output = re.split("(?<==)\s|\s(?==)",line)[0]
                            trans[current_tx].update({_output:"script: "})
                            #skip line of "value" and "script = '\n"
                            #first line of this input's script
                            l += 3
                            line = raw_dump[l]
                            line = line.lstrip()
                            #write all the script to its ocrresponding input
                            while not line == "'\n":
                                trans[current_tx][_output]+=line
                                l += 1
                                line = raw_dump[l]
                                line = line.lstrip()
                            #get output scriptType
                            while not line == "}\n":
                                l += 1
                                line = raw_dump[l]
                                line = line.lstrip()
                                if "scriptType =" in line:
                                    if not re.split("(?<==)\s|\s(?==)",line)[2] in ex_list:
                                        output.write("{txHash:%s}\n"%(trans[current_tx]["txHash"]))


        #print trans


if __name__ == '__main__':
    main()
