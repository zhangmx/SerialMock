import ast,sys

generated_template = """
#autogenerated by serial_mock
from itertools import cycle
from serial_mock import Serial,serial_query
import logging
logger = logging.getLogger("serial_mock")

class MySerial(Serial):
    prompt = ""
    endline = ""
    responses = {responses}
{class_body}

if __name__ == "__main__":
   import sys
   import argparse
   parser = argparse.ArgumentParser()
   parser.add_argument("COM_PORT",help="the com port to bind this class to")
   parser.add_argument("-v","--verbose",help="verbose mode enabled",choices=["ERROR","WARN","DEBUG","INFO"],nargs="?")
   args = parser.parse_args()
   if args.verbose:
      logger.setLevel(getattr(logging,args.verbose,logging.WARN))
   MySerial(args.COM_PORT).MainLoop()
"""
function_template = """
    @serial_query("{query}")
    def {fn_name}(self):
        return next(self.responses["{query}"])
"""
def _parseBridgeFile(fname):
    tmp = None
    close = False
    response_data = {}
    empty_rules = []
    directions = {}
    if isinstance(fname,basestring):
        fname = open(fname,"rb")
        close=True
    try:
        for line in fname:
            if tmp is None:
                tmp = line

            elif line.startswith(tmp[0]):
                empty_rules.append(ast.literal_eval(tmp[1:-1]).strip())
                tmp = line
            else:
                key = ast.literal_eval(tmp[1:-1]).strip()
                directions[key]=tmp[0]
                response_data.setdefault(key,[]).append(ast.literal_eval(line[1:-1]).strip())
                tmp = None
        empty_rules = filter(None,empty_rules)
        if any(empty_rules):
            print "Warning Found The Following Empty Rules"
            print empty_rules

        return response_data,empty_rules,directions
    finally:
        if close:
            fname.close()

def convertBridgeFileToInterface(fname,outfile):
    answer_response,empty_rules,directionality = _parseBridgeFile(fname)
    functions = ""
    _responses = "{"
    for i,(key,responses) in enumerate(answer_response.items(),1):
        _responses += '"%s":cycle(%s),'%(key,responses)

        functions += function_template.format(fn_name="response_handler%d"%i,query=key)
    _responses += "}"
    if isinstance(outfile,basestring):
        with open(outfile,"wb") as f:
            f.write(generated_template.format(class_body=functions,responses=_responses))
    else:
        outfile.write(generated_template.format(class_body=functions,responses=_responses))



