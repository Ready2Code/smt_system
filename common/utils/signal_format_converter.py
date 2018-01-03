import json
from datetime import datetime

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)

#-------------------------------------- program.json to mmt message.json ------------------------------------

def load(name):
    with open(name) as json_file:
        data = json.load(json_file)
        return data

def create_PA_table(program):
    PA_table = {}
    PA_table["table_id"] = 0
    PA_table["version"] = 0
    return PA_table

def create_CEU_consumption_descriptor(resource):
    CEU_consumption_descriptor = {}
    CEU_consumption_descriptor["descriptor_tag"] = 0x1001
    pass

def create_additional_descriptor(resource):
    additional_descriptor = {}
    additional_descriptor["descriptor_tag"] = 0x2001
    additional_content= {}
    additional_content["begin"] = resource["begin"]
    additional_content["end"]   = resource["end"]
    additional_content["sequence"]   = resource["sequence"]    
    additional_content["poster"]   = resource["poster"] if resource.has_key("poster") else ""    
    additional_content["type"]   = resource["type"]    
    additional_content["added"]   = resource["added"]   if resource.has_key("added") else "true" 
    descriptor_byte   = json.dumps(additional_content, cls=DateTimeEncoder)
    additional_descriptor["descriptor_byte"] = descriptor_byte
    return additional_descriptor

def create_CEU_consumption_descriptor(resource, layer_id):
    CEU_consumption_descriptor = {}
    CEU_consumption_descriptor["descriptor_tag"] = 0x1001
    CEU_consumption_descriptor["CEUS"]= []
    CEU = {}
    CEU["CEU_sequence_number"] = 0
    CEU["layer"]=[]
    CEU["layer"].append({"layer_id":layer_id})
    CEU["layer_exchange_flag"] = 0
    CEU["layer_copy_flag"] = 0  
    CEU_consumption_descriptor["CEUS"].append(CEU)
    return CEU_consumption_descriptor


def create_MP_table(program):
    MP_table = {}
    MP_table["table_id"] = 0x20  #Complete MP table
    MP_table["version"] = 0 
    MP_table["MP_table_mode"] = 0x10   #independent_processing_mode    
    MP_table["MMT_package_id"] = 0
    MP_table["assets"] = []
    for i in range(len(program["resources"])):
        resource = program["resources"][i]
        asset = {}
        asset["Identifier_mapping"] = {}
        asset["Identifier_mapping"]["identifier_type"] = 0x00 #asset_id
        asset["Identifier_mapping"]["asset_id"] = {}
        asset["Identifier_mapping"]["asset_id"]["asset_id_scheme"] = "UUID"
        asset["Identifier_mapping"]["asset_id"]["asset_id_byte"] = resource["id"]
        asset["asset_type"] = "MMPU"
        asset["asset_clock_relation_flag"] = 0
        asset["asset_location"] = [] 
        MMT_general_location_info = {}
        MMT_general_location_info["location_type"] = 0x05 #URL
        MMT_general_location_info["URL_byte"] = resource["url"]
        asset["asset_location"].append(MMT_general_location_info)
        if resource.has_key("bk"):
            MMT_general_location_info = {}
            MMT_general_location_info["location_type"] = 0x05 #URL
            MMT_general_location_info["URL_byte"] = resource["url"]
            asset["asset_location"].append(MMT_general_location_info)            
        #---------asset_descriptors---------------
        asset["asset_descriptors"] = [] 
        CEU_consumption_descriptor = create_CEU_consumption_descriptor(resource, i)
        asset["asset_descriptors"].append(CEU_consumption_descriptor)

        additional_descriptor = create_additional_descriptor(resource)
        asset["asset_descriptors"].append(additional_descriptor)
        MP_table["assets"].append(asset)
    return MP_table


def percentage_to_int8(p_str):
    f = float(p_str.replace("%",""))/100;
    return int(f * 255)

def create_Layer_display_table(program):
    Layer_display_table = {}
    Layer_display_table["table_id"] = 0x80  
    Layer_display_table["version"] = 0 
    Layer_display_table["layer"] = []
    for i in range(len(program["resources"])):
        resource = program["resources"][i]
        layer = {}
        layer["layer_id"] = i
        layer["device_id"] = 0
        layer["width"] = percentage_to_int8(resource["layout"]["width"])
        layer["height"] = percentage_to_int8(resource["layout"]["height"])
        layer["center_x"] = percentage_to_int8(resource["layout"]["posx"]) +  layer["width"]/2
        layer["center_y"] = percentage_to_int8(resource["layout"]["posy"]) +  layer["height"]/2  
        layer["display_order"] = 0
        layer["fitting_type"] = 0
        layer["adjust_enable_flag"] = 0
        layer["transparency"] = 0     
        Layer_display_table["layer"].append(layer)
    return  Layer_display_table 

def create_MPI_table(program):
    pass

def program_to_PA_message(program, key):
    PA_message = {}

    PA_message["message_id"] = 0
    PA_message["version"] = program["sequence"]

    PA_message["extension"] = []
    PA_message["message_payload"] = []   
     
    PA_table = create_PA_table(program)
    PA_message["extension"].append({"table_id":PA_table["table_id"],"table_version":PA_table["version"]})
    PA_message["message_payload"].append(PA_table)

    MP_table = create_MP_table(program)
    PA_message["extension"].append({"table_id":MP_table["table_id"],"table_version":MP_table["version"]})
    PA_message["message_payload"].append(MP_table)


    Layer_display_table = create_Layer_display_table(program)
    PA_message["extension"].append({"table_id":Layer_display_table["table_id"],"table_version":Layer_display_table["version"]})
    PA_message["message_payload"].append(Layer_display_table)
    if key == '':
        return PA_message
    else:
        return {key:PA_message}
    #print json.dumps(PA_message, indent=4)

#-------------------------------------- mmt  message josn to program.json ------------------------------------


def parse_MP_table(MP_table):
    resources = []
    for asset in MP_table["assets"]:
        resource = {}
        resource["id"] = asset["Identifier_mapping"]["asset_id"]["asset_id_byte"]
        resource["url"] = asset["asset_location"][0]["URL_byte"]
        if len(asset["asset_location"]) > 1:
            resource["url"] = asset["asset_location"][1]["URL_byte"]
        for descriptor in asset["asset_descriptors"]:
            if descriptor["descriptor_tag"] == 0x2001:
                parse_additional_descriptor(descriptor, resource)
            elif descriptor["descriptor_tag"] == 0x1001:
                parse_CEU_consumption_descriptor(descriptor, resource)
        resources.append(resource)
    return resources

def parse_CEU_consumption_descriptor(CEU_consumption_descriptor, resource):
    resource["layer_id"] = CEU_consumption_descriptor["CEUS"][0]["layer"][0]["layer_id"]

def parse_Layer_display_table(Layer_display_table, program):
    for layer in Layer_display_table["layer"]:
        for resource in program["resources"]:
            if layer["layer_id"] == resource["layer_id"]:
                resource["layout"] = {}
                resource["layout"]["width"] = "%f" % (100.0 * layer["width"] / 255) +"%"
                resource["layout"]["height"] = "%f" % (100 * layer["height"] / 255) +"%"
                resource["layout"]["posx"] = "%f" % (100 * (layer["center_x"] - layer["width"] /2 ) / 255) +"%"
                resource["layout"]["posy"] = "%f" % (100 * (layer["center_y"] - layer["height"] /2 ) / 255) +"%"
                break



def parse_additional_descriptor(additional_descriptor, resource):
    additional_content = {}
    additional_content = json.loads(additional_descriptor["descriptor_byte"])
    resource["begin"] = additional_content["begin"]
    resource["end"]   = additional_content["end"]  
    resource["sequence"]  = additional_content["sequence"]     
    resource["poster"] = additional_content["poster"]   if additional_content.has_key("poster") else ""    
    resource["type"]   = additional_content["type"] 
    resource["added"] = additional_content["added"]  if additional_content.has_key("added") else "true"




def PA_message_to_program(PA_message, key=''):
    root = {}
    root["programmer"] = {}
    program = root["programmer"]
    program["sequence"] = PA_message["version"]
    for table in PA_message["message_payload"]:
        if table["table_id"] == 0x20:
            program["resources"] = parse_MP_table(table)

    #------------------second step parse--------------------------
    for table in PA_message["message_payload"]:
        if table["table_id"] == 0x80:
            parse_Layer_display_table(table, program)

    program["begin"] = program["resources"][0]["begin"]
    program["end"] = program["resources"][0]["end"] 
    if key == '':
        return root
    else:
        return {key:root}


#------------------------------------------------------------
if __name__ == '__main__':
    json_data = load("program.json")
    print json.dumps(json_data, indent=4)
    PA_message = program_to_PA_message(json_data["programmer"])
    print "------------------------------------------------------"
    print json.dumps(PA_message, indent=4)  
    print "------------------------------------------------------"    
    programmer = PA_message_to_program(PA_message)
    print json.dumps(programmer, indent=4)    
