# coding=utf-8
import csv
import sys
import traceback

from logger import DebugLogger

class Csv_Parser:

    def read_file_and_process(self, file_url):
        with open(file_url) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            with open('data/last version/TripletPreparedByProgram-bushra.csv', 'w', newline='') as myfile:
                wr = csv.writer(myfile, delimiter=',')
                for row in csv_reader:
                    try:
                        # if(row[2].capitalize().rstrip().lstrip()=="Has crpd definition"):
                        #     wr.writerow([row[0],row[1], "has definition","BN"+str(line_count)])
                        #     wr.writerow([row[0], "BN"+str(line_count), "has definition", row[3]])
                        #     wr.writerow([row[0], "BN"+str(line_count), "according to", "Crpd article "+str(row[0])])
                        #
                        # elif(row[2].capitalize().rstrip().lstrip()=="Has wikidata definition"):
                        #     wr.writerow([row[0],row[1], "has definition","BN"+str(line_count)])
                        #     wr.writerow([row[0], "BN"+str(line_count), "has definition", row[3]])
                        #     wr.writerow([row[0], "BN"+str(line_count), "according to", "Wikidata"])
                        #
                        # elif (row[2].capitalize().rstrip().lstrip() == "Mentioned in crpd article"):
                        #     wr.writerow([row[0], row[1], "mentioned in", "Crpd article "+str(row[3])])
                        #
                        # elif (row[2].capitalize().rstrip().lstrip() == "Has crpd text"):
                        #     if("Crpd" in row[1].capitalize().rstrip().lstrip()):
                        #         wr.writerow([row[0],row[1], "has text", row[3]])
                        #     else:
                        #         wr.writerow([row[0], row[1], "has text related", "BN" + str(line_count)])
                        #         wr.writerow([row[0], "BN" + str(line_count), "has text related", row[3]])
                        #         wr.writerow([row[0], "BN" + str(line_count), "has origin", "Crpd article " + str(row[0])])
                        # else:
                        #     wr.writerow([row[0], row[1], row[2].lower(),row[3]])
                        if (row[2].capitalize().rstrip().lstrip() == "Has crpd definition"):
                            wr.writerow([row[0], row[1], "has definition", row[3].rstrip().lstrip(),"according to","Crpd article " + str(row[0])])

                        elif (row[2].capitalize().rstrip().lstrip() == "Has wikidata definition"):
                            wr.writerow([row[0], row[1], "has definition", row[3].rstrip().lstrip(),"according to","Wikidata"])

                        elif (row[2].capitalize().rstrip().lstrip() == "Mentioned in crpd article"):
                            wr.writerow([row[0], row[1], "mentioned in", "Crpd article " + str(row[3])])

                        elif (row[2].capitalize().rstrip().lstrip() == "Has definition (disability wiki)"):
                            wr.writerow([row[0], row[1], "has definition", row[3].rstrip().lstrip(),"according to","Disability rights wiki"])

                        elif (row[2].capitalize().rstrip().lstrip() == "Has crpd text"):
                            if ("Crpd" in row[1].capitalize().rstrip().lstrip()):
                                wr.writerow([row[0], row[1], "has text", row[3]])
                            else:
                                "Ex : Health >> has text related >> text >> (text)has origin>> crpd article 12"
                                wr.writerow([row[0], row[1], "has text related", row[3].rstrip().lstrip(), "has origin", "Crpd article " + str(row[0])])
                        else:
                            wr.writerow([row[0], row[1], row[2].lower(), row[3]])

                    except Exception as e:
                        print(e)
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        tb = traceback.extract_tb(exc_tb)[-1]
                        err_msg = f"ERROR : CSV_CLEAN_.:{type(self).__name__} Concept : {row[1].rstrip()} ,>> Property : {row[2].rstrip()}  row count : {line_count}, MESSSAGE >> {e}"
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        tb = traceback.extract_tb(exc_tb)[-1]
                        err_trace = f"ERROR_TRACE >>>: + {exc_type} , method: {tb[2]} , line-no: {tb[1]}"
                        logger = DebugLogger();
                        logger.logError('CREATE_CLAIM_V2', e, exc_type, exc_obj, exc_tb, tb, err_msg)
                    line_count += 1
                myfile.close()

def start():
    csv_Parser = Csv_Parser()
    # csv_Parser.read_file_and_process('data/TripletsClean.csv')
    csv_Parser.read_file_and_process('data/last version/2021.04.12 - Ontology Approach - Bushra.csv')

start()
exit()