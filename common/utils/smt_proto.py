import time
import socket
import struct
import sys
import json
import platform
def get_platform():
    try:
        import starglobal
        return starglobal.platform
    except:
        return platform.system()
if get_platform() != 'Android':
    print "reload sys"
    reload(sys)
    sys.setdefaultencoding('utf-8')
else:
    print "NOTIFY: reload(sys) is disable here, if smt_proto do not work, pls check here"
SMTP_HEADER_LENGTH = 16
SMTP_PAYLOAD_HEADER_LENGTH = 4
SMT_MESSAGE_HEADER_LENGTH = 7
SMT_TABLE_HEADER_LENGTH = 4
SUBSET_0_MPT_TABLE_ID = 0x11
(VCFECrXR, smtp_header_flags, packet_id, timestamp, packet_sequence_number, packet_counter) = range(0, 6)
(smtp_payload_flags, frag_counter, MSG_length) = range(0, 3)
(message_id, message_version, message_length) = range(0, 3)
(table_id, table_version, table_length) = range(0, 3)



class SmtProto:
    def __init__(self):
        self.count = 0
        self.message_data = ''
        self.message = {}

    def init_socket(self, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', port))


    def process_smtp_data(self,data):
        self.data = data
        self.count = 0
        self.smtp_header_parser()
        return self.smtp_payload_parser()

    def recv_smtp_data(self):
        while 1:
            data, address = self.sock.recvfrom(4096)
            if self.process_smtp_data(data):
                print json.dumps(self.message, indent=4)
            time.sleep(0.1)

    def smtp_header_parser(self):
        self.smtp_header = struct.unpack("!BBHIII", self.data[:SMTP_HEADER_LENGTH])
        self.count = SMTP_HEADER_LENGTH

    def smt_pa_table_parser(self, offset, cur_node):
        #PA Table
        (number_of_tables,) = struct.unpack("!B", self.message_data[offset:offset+1])
        offset = offset + 1
        for i in range(0, number_of_tables):
            pass 
        return offset       

    def smt_asset_parser(self, offset, asset_node):
        (asset_id_scheme,asset_id_length) = struct.unpack("!4sB", self.message_data[offset:offset+5])
        offset = offset + 5
        (asset_id_byte,) = struct.unpack("!"+"%ds" % asset_id_length, self.message_data[offset:offset+asset_id_length]) 
        offset = offset + asset_id_length
        asset_node["asset_id_scheme"] = asset_id_scheme
        asset_node["asset_id_byte"] = asset_id_byte
        return offset     


    def smt_Identifier_mapping_parser(self, offset, Identifier_mapping_node):
        (identifier_type,) = struct.unpack("!B", self.message_data[offset:offset+1])
        offset = offset + 1
        Identifier_mapping_node["identifier_type"] = identifier_type

        if identifier_type == 0x00:
            #asset_id
            Identifier_mapping_node["asset_id"] = {}
            offset = self.smt_asset_parser(offset, Identifier_mapping_node["asset_id"])
            pass
        elif identifier_type == 0x01:
            pass
        else:
            pass
        return offset


    def MMT_general_location_info(self, offset, general_location_info_node):
        (location_type,) = struct.unpack("!B", self.message_data[offset:offset+1])
        offset = offset + 1    
        general_location_info_node["location_type"] =location_type
        if location_type == 0x00:
            #packet id
            pass
        elif location_type == 0x05:
            (URL_length,) = struct.unpack("!B", self.message_data[offset:offset+1])
            offset = offset + 1             
            (URL_byte,) = struct.unpack("!%ds"%URL_length, self.message_data[offset:offset+URL_length])            
            offset = offset + URL_length
            general_location_info_node["URL_byte"] =URL_byte
        return offset


    def smt_MPU_Timestamp_descriptor_parser(self, offset,  descriptor_node):
        (length,) = struct.unpack("!B", self.message_data[offset:offset+1])
        offset = offset + 1
        descriptor_node["descriptor"] = []
        descriptor_node["length"] = length
        for i in range(0, length/12):
            (mpu_sequence_number, mpu_presentation_time) = struct.unpack("!IQ", self.message_data[offset:offset+12])
            offset = offset + 12
            descriptor_node["descriptor"].append({"mpu_sequence_number":mpu_sequence_number, "mpu_presentation_time":mpu_presentation_time})
        return offset

    def smt_CEU_Consumption_descriptor_parser(self, offset, descriptor_node):
        (length,) = struct.unpack("!H", self.message_data[offset:offset+2])
        offset = offset + 2
        (number_of_CEUs,) = struct.unpack("!B", self.message_data[offset:offset+1])
        offset = offset + 1
        descriptor_node["CEUS"] = []
        for i in range(0, number_of_CEUs):
            CEU = {}
            (CEU_sequence_number, number_of_layer) = struct.unpack("!IB", self.message_data[offset:offset+5])
            offset=offset+5
            CEU["CEU_sequence_number"] = CEU_sequence_number
            CEU["layer"] = []
            for j in range(0, number_of_layer):
                layer = {}
                (layer_id,) = struct.unpack("!B", self.message_data[offset:offset+1])
                offset = offset + 1
                layer["layer_id"] = layer_id
                CEU["layer"].append(layer)
            (flags,) = struct.unpack("!B", self.message_data[offset:offset+1])
            offset = offset + 1            
            descriptor_node["CEUS"].append(CEU)
        return offset

    def smt_additional_descriptor_parser(self, offset,  descriptor_node ):
        (length,) = struct.unpack("!H", self.message_data[offset:offset+2])
        offset = offset + 2
        (descriptor_byte,) = struct.unpack("!%ds"%length, self.message_data[offset:offset+length])
        offset=offset+length
        descriptor_node["descriptor_byte"] = descriptor_byte
        return offset

    def smt_asset_descriptor_parser(self, offset, descriptor_node):
        (descriptor_tag, ) = struct.unpack("!H", self.message_data[offset:offset+2])
        offset = offset+2
        descriptor_node["descriptor_tag"] = descriptor_tag
        if descriptor_tag == 0x02:
            # MPU Timestamp descriptor
            offset = self.smt_MPU_Timestamp_descriptor_parser(offset, descriptor_node)
        elif descriptor_tag == 0x1001:
            offset = self.smt_CEU_Consumption_descriptor_parser(offset, descriptor_node)
        elif descriptor_tag == 0x2001:
            offset = self.smt_additional_descriptor_parser(offset, descriptor_node)
        return offset



    def smt_mp_table_parser(self, offset, table_id, table_node):
        (flag,) = struct.unpack("!B", self.message_data[offset:offset+1])
        offset = offset + 1
        table_node["MP_table_mode"] =  flag & 0x03
        if table_id == SUBSET_0_MPT_TABLE_ID:
            pass
        (number_of_assets,) = struct.unpack("!B", self.message_data[offset:offset+1])
        offset = offset + 1
        assets = []
        table_node["number_of_assets"] = number_of_assets
        for i in range(0, number_of_assets):
            asset = {}
            asset["Identifier_mapping"] = {}
            offset = self.smt_Identifier_mapping_parser(offset, asset["Identifier_mapping"])
            (asset_type,) = struct.unpack("!4s", self.message_data[offset:offset+4])
            offset = offset + 4 
            asset["asset_type"] = asset_type
            (flag,) = struct.unpack("!B", self.message_data[offset:offset+1])
            offset = offset + 1             
            asset["asset_clock_relation_flag"] = flag & 0x01
            asset["asset_location"] = []
            (location_count,) = struct.unpack("!B", self.message_data[offset:offset+1])
            offset = offset + 1
            for j in range(0, location_count):
                location = {}
                offset = self.MMT_general_location_info(offset, location)
                asset["asset_location"].append(location)
            asset["asset_descriptors"] = [] 
            (asset_descriptors_length,) = struct.unpack("!H", self.message_data[offset:offset+2])
            offset = offset + 2
            asset_descriptors_end = offset + asset_descriptors_length
            while offset < asset_descriptors_end:
                asset_descriptor_node = {}
                offset = self.smt_asset_descriptor_parser(offset, asset_descriptor_node)
                asset["asset_descriptors"].append(asset_descriptor_node)
            #(asset_descriptors_byte,) = struct.unpack("!%ds"%asset_descriptors_length, self.message_data[offset:offset+asset_descriptors_length])            
            #offset=offset+asset_descriptors_length
            assets.append(asset)
        table_node["assets"] = assets
        return offset


    def smt_Layer_display_table_parser(self, offset, table_node):
        (number_of_layer,) = struct.unpack("!B", self.message_data[offset:offset+1])
        offset = offset + 1
        table_node["layer"] = []
        for i in range(0, number_of_layer):
            layer = {}
            (layer_id,device_id,center_x,center_y,width,height,display_order,flags, transparency) = struct.unpack("!BBBBBBBBB", self.message_data[offset: offset+9])
            offset = offset + 9
            layer["layer_id"] = layer_id
            layer["device_id"] = device_id
            layer["center_x"] = center_x
            layer["center_y"] = center_y
            layer["width"] = width
            layer["height"] = height
            layer["display_order"] = display_order
            layer["transparency"] = transparency
            table_node["layer"].append(layer)     

        return offset

    def smt_table_parser(self, offset, root_node):
        table_header = struct.unpack("!BBH", self.message_data[offset: offset+SMT_TABLE_HEADER_LENGTH])
        offset=offset+SMT_TABLE_HEADER_LENGTH
        table = {}
        table["table_id"] = table_header[table_id]
        table["version"] = table_header[table_version]        
        table["length"] = table_header[table_length] 
        if table_header[table_id] == 0x00:
            offset = self.smt_pa_table_parser(offset, table)
        elif 0x11 <= table_header[table_id] and table_header[table_id] <= 0x20:
            offset = self.smt_mp_table_parser(offset, table_header[table_id], table)
        elif table_header[table_id] == 0x80:
            offset = self.smt_Layer_display_table_parser(offset, table)
        root_node.append(table)
        return offset


    def smt_pa_message_parser(self, offset, PA_message):
        (number_of_tables,) = struct.unpack("!B", self.message_data[offset:offset+1])
        offset = offset + 1
        PA_message["extension"] = []
        for i in range(0, number_of_tables):
            nlen =  4
            tt = struct.unpack("!BBH", self.message_data[offset:offset+nlen])
            offset = offset + nlen
            table = {}
            table["table_id"]      = tt[0]    
            table["table_version"] = tt[1]
            table["table_length"]  = tt[2]    
            PA_message["extension"].append(table)
        PA_message["message_payload"] = []
        for i in range(0, number_of_tables):
            offset = self.smt_table_parser(offset, PA_message["message_payload"])
        return offset



    def smt_message_parser(self):
        length = len(self.message_data)
        offset = 0       
        while offset < length:
            message_header = struct.unpack("!HBI", self.message_data[offset: offset + SMT_MESSAGE_HEADER_LENGTH])
            offset = offset + SMT_MESSAGE_HEADER_LENGTH
            if message_header[message_id] == 0:
                #pa message
                self.message["PA_message"] = {}
                self.message["PA_message"]["message_id"] = 0  
                self.message["PA_message"]["version"] =   message_header[message_version]          
                offset = self.smt_pa_message_parser(offset, self.message["PA_message"])
            break


    def smtp_payload_parser(self):
        self.smtp_payload_header = struct.unpack("!BBH", self.data[self.count:self.count+SMTP_PAYLOAD_HEADER_LENGTH])
        self.count = self.count+SMTP_PAYLOAD_HEADER_LENGTH
        f_i = self.smtp_payload_header[smtp_payload_flags] & 0x60
        message = self.data[self.count: self.count + self.smtp_payload_header[MSG_length]]
        if f_i == 0 or f_i == 1:
            self.message_data = ''
        self.message_data = self.message_data + message
        if f_i == 0 or f_i == 3:
            self.smt_message_parser()
            return True
        return False



#------------------------------------------------------------
if __name__ == '__main__':
    ss = SmtProto()
    ss.init_socket(9997)
    ss.recv_smtp_data()
