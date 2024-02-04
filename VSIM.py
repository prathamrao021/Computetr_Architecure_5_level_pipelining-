import sys

def twos_complement_to_decimal(binary_string):
    if binary_string[0] == '1':
        # If the most significant bit is 1, it's a negative number in two's complement
        # Perform two's complement operation
        inverted_bits = ''.join('1' if bit == '0' else '0' for bit in binary_string)
        decimal_value = -(int(inverted_bits, 2) + 1)
    else:
        # If the most significant bit is 0, it's a positive number
        decimal_value = int(binary_string, 2)
    return decimal_value

class Instruction:
    def __init__(self, binary):
        self.binary = binary
        self.inst_count = None
        self.category = None
        self.type = None
        self.active = False
        self.source_1 = None
        self.source_2 = None
        self.destination = None
        self.immediate = None
        self.inst_print = None
        self.stop_moving = False
        self.temp_ans = None
        self.is_first_sw = False
        self.is_branch = False
        self.is_logical = False
        self.is_arithematic = False
        self.is_sw_or_lw = False
        self.find_category()
        self.find_type()
        self.find_src_and_dest_and_imm()
        self.get_instruction_print()

    def find_category(self):
        temp_cat = self.binary[30:32]
        if temp_cat == "00":
            self.category = 1   
        elif temp_cat == "01":
            self.category = 2
        elif temp_cat == "10":
            self.category = 3
        elif temp_cat == "11":
            self.category = 4
    
    def find_type(self) -> str:
        temp_type = self.binary[25:30]
        if self.category == 1:
            if temp_type == "00000":
                self.type = "beq"
                self.is_branch = True
            elif temp_type == "00001":
                self.type = "bne"
                self.is_branch = True
            elif temp_type == "00010":
                self.type = "blt"
                self.is_branch = True
            elif temp_type == "00011":
                self.type = "sw"
                self.is_sw_or_lw = True

        elif self.category == 2:
            if temp_type == "00000":
                self.type = "add"
                self.is_arithematic = True
            elif temp_type == "00001":
                self.type = "sub"
                self.is_arithematic = True
            elif temp_type == "00010":
                self.type = "and"
                self.is_logical = True
            elif temp_type == "00011":
                self.type = "or"
                self.is_logical = True

        elif self.category == 3:
            if temp_type == "00000":
                self.type = "addi"
                self.is_arithematic = True
            elif temp_type == "00001":
                self.type = "andi"
                self.is_logical = True                
            elif temp_type == "00010":
                self.type = "ori"
                self.is_logical = True
            elif temp_type == "00011":
                self.type = "sll"
                self.is_logical = True
            elif temp_type == "00100":
                self.type = "sra"
                self.is_logical = True
            elif temp_type == "00101":
                self.type = "lw"
                self.is_sw_or_lw = True

        elif self.category == 4:
            if temp_type == "00000":
                self.type = "jal"
                self.is_branch = True
            elif temp_type == "11111":
                self.type = "break"
    
    def find_src_and_dest_and_imm(self):
        if self.category == 1:
            self.source_1 = int(self.binary[12:17], 2)
            self.source_2 = int(self.binary[7:12], 2)
            self.immediate = twos_complement_to_decimal(self.binary[0:7]+self.binary[20:25])
        elif self.category == 2:
            self.source_1 = int(self.binary[12:17], 2)
            self.source_2 = int(self.binary[7:12], 2)
            self.destination = int(self.binary[20:25], 2)
        elif self.category == 3:
            self.source_1 = int(self.binary[12:17], 2)
            self.destination = int(self.binary[20:25], 2)
            self.immediate = twos_complement_to_decimal(self.binary[0:12])
        elif self.category == 4:
            self.immediate = twos_complement_to_decimal(self.binary[0:20])
            self.destination = int(self.binary[20:25], 2)
    
    def get_instruction_print(self):
        if self.category == 1:
            if self.type == "beq" or self.type == "bne" or self.type == "blt":
                self.inst_print = self.type+" x"+str(self.source_1)+", x"+str(self.source_2)+", #"+str(self.immediate)
            elif self.type == "sw":
                self.inst_print = "sw "+"x"+str(self.source_1)+", "+str(self.immediate)+"(x"+str(self.source_2)+")"
        elif self.category == 2:
            self.inst_print = self.type+" x"+str(self.destination)+", x"+str(self.source_1)+", x"+str(self.source_2)
        elif self.category == 3:
            if self.type == "addi" or self.type == "andi" or self.type == "ori" or self.type == "sll" or self.type == "sra":
                self.inst_print = self.type+" x"+str(self.destination)+", x"+str(self.source_1)+", #"+str(self.immediate)
            elif self.type == "lw":
                self.inst_print = "lw "+"x"+str(self.destination)+", "+str(self.immediate)+"(x"+str(self.source_1)+")"
        elif self.category == 4:
            if self.type == 'jal':
                self.inst_print = "jal "+"x"+str(self.destination)+", #"+str(self.immediate)
            elif self.type == 'break':
                self.inst_print = "break"

class Buffer:
    def __init__(self, size):
        self.size = size
        self.buffer = []
        self.first_sw = False
        self.is_waiting = None
    
    def enqueue(self, item):
        if len(self.buffer) < self.size:
            self.buffer.append(item)
        else:
            raise Exception("Buffer full")
    
    def dequeue(self):
        if len(self.buffer) == 0:
            raise Exception("Buffer empty")
        else:
            return self.buffer.pop(0)

    def arbitrary_remove(self, index):
        if index < len(self.buffer):
            return self.buffer.pop(index)
        else:
            raise Exception("Index out of bounds")
    
    def is_empty(self):
        if (len(self.buffer) == 0):
            return True
        else:
            return False

    def is_full(self):
        if (len(self.buffer) == self.size):
            return True
        else:
            return False
class Processing:
    def __init__(self):
        self.memory_stack = {}
        self.instruction_stack = {}
        self.register_stack = [0]*32
        self.program_end = None
        self.all_instructions = {}
        self.program_counter = 256
        self.break_instruction_count = 0
        self.stop_fetch = False
        self.is_inst_dep = False
        self.is_structural_dep = False
        self.active_inst_list = []
        self.cycle = 1
        self.process_alu1 = True
        self.process_alu2 = True
        self.process_alu3 = True
        self.stop = False
        self.next_fetch = True
        
        self.l_pre_issue = Buffer(4)
        self.r_pre_issue = Buffer(4)

        self.l_pre_alu1 = Buffer(2)
        self.r_pre_alu1 = Buffer(2)

        self.l_pre_alu2 = Buffer(1)
        self.r_pre_alu2 = Buffer(1)
        self.l_post_alu2 = Buffer(1)
        self.r_post_alu2 = Buffer(1)

        self.l_pre_alu3 = Buffer(1)
        self.r_pre_alu3 = Buffer(1)
        self.l_post_alu3 = Buffer(1)
        self.r_post_alu3 = Buffer(1)

        self.l_pre_mem = Buffer(1)
        self.r_pre_mem = Buffer(1)
        self.l_post_mem = Buffer(1)
        self.r_post_mem = Buffer(1)

        self.exec = Buffer(1)
        self.wait = Buffer(1)
    

    # def dependency_check(self, inst_list, curr_inst):
    #     for i in inst_list:
    #         #RAW
    #         if(curr_inst.source_1 != None and curr_inst.source_1 == i.destination):
    #             return True
    #         if(curr_inst.source_2 != None and curr_inst.source_2 == i.destinatoion):
    #             return True
    #         #Pre issue is full
    #         if(len(self.pre_issue)==self.pre_issue.size):
    #             return True
    
    def dependency_check(self, inst_list, curr_inst):
        for i in inst_list:
            if(curr_inst.source_1 != None and i.destination != None and curr_inst.source_1 == i.destination):
                return True
            if(curr_inst.source_2 != None and i.destination != None and curr_inst.source_2 == i.destination):
                return True
            if(curr_inst.destination != None and i.destination != None and curr_inst.destination == i.destination):
                return True
            if(curr_inst.destination != None and i.source_1 != None and curr_inst.destination == i.source_1):
                return True
            if(curr_inst.destination != None and i.source_2 != None and curr_inst.destination == i.source_2):
                return True
        return False

    def structural_dependency(self, curr_inst):
        if(curr_inst.is_logical and self.r_pre_alu3.is_full()):
            return True
        elif(curr_inst.is_arithematic and self.r_pre_alu2.is_full()):
            return True
        elif(curr_inst.is_sw_or_lw and self.r_pre_alu1.is_full()):
            return True
        return False
    
    def process_branch(self, instruction_1):
        if(instruction_1.type == 'jal'):
            self.register_stack[instruction_1.destination] = self.program_counter + 4
            self.program_counter += instruction_1.immediate * 2
        elif(instruction_1.type == 'beq'):
            if(self.register_stack[instruction_1.source_1] == self.register_stack[instruction_1.source_2]):
                self.program_counter += (instruction_1.immediate * 2)
            else:
                self.program_counter += 4
        elif(instruction_1.type == 'bne'):
            if(self.register_stack[instruction_1.source_1] != self.register_stack[instruction_1.source_2]):
                self.program_counter += (instruction_1.immediate * 2)
            else:
                self.program_counter += 4
        elif(instruction_1.type == 'blt'):
            if(self.register_stack[instruction_1.source_1] < self.register_stack[instruction_1.source_2]):
                self.program_counter += (instruction_1.immediate * 2)
            else:
                self.program_counter += 4
    def remove_active(self, inst):
        for i in range(len(self.active_inst_list)):
            if self.active_inst_list[i].binary == inst.binary:
                self.active_inst_list.pop(i)
                break
    
    def display_cycle_registers(self, f_sim):
        f_sim.write(f"Registers")
        for i in range(32):
            if i % 8 == 0:
                f_sim.write(f"\nx{i:02d}:")
            f_sim.write(f"\t{self.register_stack[i]}")
        f_sim.write(f"\nData")
        i = 0
        for mem_ad in sorted(list(self.memory_stack.keys())):
            if i % 8 == 0:
                f_sim.write(f"\n{mem_ad}:")
            f_sim.write(f"\t{self.memory_stack[mem_ad]}")
            i+=1
        if(not self.stop):
            f_sim.write('\n')

    def print_snapshot(self,f):
        f.write('-'*20)
        f.write('\n')
        f.write(f'Cycle {self.cycle}:\n\n')
        f.write(f'IF Unit:\n')
        if len(self.wait.buffer) != 0:
            f.write(f'\tWaiting: [{self.wait.buffer[0].inst_print}]\n')
        else:
            f.write(f'\tWaiting:\n')
        if len(self.exec.buffer) == 0:
            f.write(f'\tExecuted:\n')
        else:
            f.write(f'\tExecuted: [{self.exec.buffer[0].inst_print}]\n')
        f.write('Pre-Issue Queue:\n')
        for i in range(4):
            if i < len(self.r_pre_issue.buffer):
                f.write(f'\tEntry {i}: [{self.r_pre_issue.buffer[i].inst_print}]\n')
            else:
                f.write(f'\tEntry {i}:\n')
        f.write('Pre-ALU1 Queue:\n')
        for i in range(2):
            if i < len(self.r_pre_alu1.buffer):
                f.write(f'\tEntry {i}: [{self.r_pre_alu1.buffer[i].inst_print}]\n')
            else:
                f.write(f'\tEntry {i}:\n')
        if len(self.r_pre_mem.buffer) == 0:
            f.write(f'Pre-MEM Queue:\n')
        else:
            f.write(f'Pre-MEM Queue: [{self.r_pre_mem.buffer[0].inst_print}]\n')
        if len(self.r_post_mem.buffer) == 0:
            f.write(f'Post-MEM Queue:\n')
        else:
            f.write(f'Post-MEM Queue: [{self.r_post_mem.buffer[0].inst_print}]\n')
        if len(self.r_pre_alu2.buffer) == 0:
            f.write(f'Pre-ALU2 Queue:\n')
        else:
            f.write(f'Pre-ALU2 Queue: [{self.r_pre_alu2.buffer[0].inst_print}]\n')
        if len(self.r_post_alu2.buffer) == 0:
            f.write(f'Post-ALU2 Queue:\n')
        else:
            f.write(f'Post-ALU2 Queue: [{self.r_post_alu2.buffer[0].inst_print}]\n')
        if len(self.r_pre_alu3.buffer) == 0:
            f.write(f'Pre-ALU3 Queue:\n')
        else:
            f.write(f'Pre-ALU3 Queue: [{self.r_pre_alu3.buffer[0].inst_print}]\n')
        if len(self.r_post_alu3.buffer) == 0:
            f.write(f'Post-ALU3 Queue:\n')
        else:
            f.write(f'Post-ALU3 Queue: [{self.r_post_alu3.buffer[0].inst_print}]\n')
        f.write('\n')
        self.display_cycle_registers(f)



    def fetch(self):
        #Attempt 3s
        # if self.next_fetch == False:
        #     self.next_fetch = True
        #     return
        instruction_1 = Instruction(self.all_instructions[self.program_counter])
        # self.program_counter += 4
        if len(self.l_pre_issue.buffer) + len(self.r_pre_issue.buffer) < self.l_pre_issue.size:
            if(len(self.exec.buffer) == 1):
                    inst = self.exec.dequeue()
                    # self.remove_active(inst)
            if instruction_1.type == "break" and len(self.exec.buffer) == 0 and len(self.wait.buffer) == 0:
                self.exec.enqueue(instruction_1)
                # self.program_counter += 4
                self.stop = True
                return
            if(len(self.wait.buffer)) == 1: # already an instruction is waititg and now is dependency free
                if not self.dependency_check(self.active_inst_list, instruction_1) and not self.dependency_check(self.r_pre_issue.buffer, instruction_1):
                    instruction_1 = self.wait.dequeue()
                    self.exec.enqueue(instruction_1)
                    self.process_branch(instruction_1)
                    # self.stop_fetch = True
                return
            self.is_inst_dep = self.dependency_check(self.active_inst_list, instruction_1) or self.dependency_check(self.r_pre_issue.buffer, instruction_1)
            self.is_structural_dep = False if len(self.r_pre_issue.buffer) + len(self.l_pre_issue.buffer) + len(self.exec.buffer) + len(self.wait.buffer) < 4 else True
            # self.active_inst_list.append(instruction_1)
            if(instruction_1.is_branch):
                if(self.is_inst_dep):
                    self.wait.enqueue(instruction_1)
                    # self.active_inst_list.append(instruction_1)
                    # self.stop_fetch = True
                else:
                    self.exec.enqueue(instruction_1)
                    self.process_branch(instruction_1)
                    # self.active_inst_list.append(instruction_1)
            else:
                self.l_pre_issue.enqueue(instruction_1)
                # self.active_inst_list.append(instruction_1)
                self.program_counter += 4
                if len(self.l_pre_issue.buffer) + len(self.r_pre_issue.buffer) < self.l_pre_issue.size:
                    instruction_2 = Instruction(self.all_instructions[self.program_counter])
                    if len(self.l_pre_issue.buffer) == self.l_pre_issue.size:
                        return
                    self.is_inst_dep = self.dependency_check(self.active_inst_list, instruction_2) or self.dependency_check(self.r_pre_issue.buffer, instruction_2)
                    self.is_structural_dep = False if len(self.r_pre_issue.buffer) + len(self.l_pre_issue.buffer) <= 4 else True
                    # self.active_inst_list.append(instruction_2)
                    if(instruction_2.is_branch):
                        if(self.is_inst_dep):
                            self.wait.enqueue(instruction_2)
                            # self.active_inst_list(instruction_2)
                            # self.stop_fetch = True
                        else:
                            self.exec.enqueue(instruction_2)
                            self.process_branch(instruction_2)
                            # self.active_inst_list.append(instruction_2)
                    else:
                        self.l_pre_issue.enqueue(instruction_2)
                        # self.active_inst_list.append(instruction_2)
                        self.program_counter += 4
        # if len(self.l_pre_issue.buffer) + len(self.r_pre_issue.buffer) == 4:
        #     self.next_fetch = False
        #     return
        
    def issue(self):
        is_memory_loaded = False
        is_store_loaded = False
        i = 0
        while i < len(self.r_pre_issue.buffer):
            #shouldn't we check for r_pre_alu for structural dependency
            self.is_structural_dep = self.structural_dependency(self.r_pre_issue.buffer[i])
            self.is_inst_dep = self.dependency_check(self.r_pre_issue.buffer[0:i], self.r_pre_issue.buffer[i]) or self.dependency_check(self.active_inst_list, self.r_pre_issue.buffer[i])
            if(not self.is_inst_dep and not self.is_structural_dep):
                if(self.r_pre_issue.buffer[i].is_sw_or_lw) and not is_memory_loaded and not is_store_loaded:
                    if(self.r_pre_issue.buffer[i].type == "sw"):
                        is_store_loaded = True
                        is_memory_loaded = True
                    elif(self.r_pre_issue.buffer[i].type == "lw"):
                        is_memory_loaded = True
                    self.active_inst_list.append(self.r_pre_issue.buffer[i])
                    self.l_pre_alu1.enqueue(self.r_pre_issue.arbitrary_remove(i))
                    # i += 1
                elif(self.r_pre_issue.buffer[i].is_arithematic):
                    if self.process_alu2:
                        self.process_alu2 = False
                        self.active_inst_list.append(self.r_pre_issue.buffer[i])
                        self.l_pre_alu2.enqueue(self.r_pre_issue.arbitrary_remove(i))
                    else:
                        self.process_alu2 = True
                        i += 1
                elif(self.r_pre_issue.buffer[i].is_logical):
                    if self.process_alu3:
                        self.process_alu3 = False
                        self.active_inst_list.append(self.r_pre_issue.buffer[i])
                        self.l_pre_alu3.enqueue(self.r_pre_issue.arbitrary_remove(i))
                    else:
                        self.process_alu3 = True
                        i += 1
                else:
                    i += 1
            elif(self.r_pre_issue.buffer[i].type == "sw"):
                is_store_loaded = True
                i += 1
            else:
                i += 1
        self.process_alu2 = True if self.l_pre_alu2.is_empty() else False
        self.process_alu3 = True if self.l_pre_alu3.is_empty() else False

    def alu1(self):
        if len(self.r_pre_alu1.buffer) > 0:
            instruction_1 = self.r_pre_alu1.dequeue()
            if instruction_1.type == "lw":
                instruction_1.temp_ans = self.memory_stack[instruction_1.immediate + self.register_stack[instruction_1.source_1]]
            elif instruction_1.type == "sw":
                #DO that in mem function
                pass
            
            if len(self.l_pre_mem.buffer) < self.l_pre_mem.size:
                self.l_pre_mem.enqueue(instruction_1)
        else:
            pass

    def alu2(self):
        if len(self.r_pre_alu2.buffer) > 0:
            instruction_2 = self.r_pre_alu2.dequeue()
            if instruction_2.type == "add":
                instruction_2.temp_ans = self.register_stack[instruction_2.source_1] + self.register_stack[instruction_2.source_2]
            elif instruction_2.type == "sub":
                instruction_2.temp_ans = self.register_stack[instruction_2.source_1] - self.register_stack[instruction_2.source_2]
            elif instruction_2.type == "addi":
                instruction_2.temp_ans = self.register_stack[instruction_2.source_1] + instruction_2.immediate

            if len(self.l_post_alu2.buffer) < self.l_post_alu2.size:
                 self.l_post_alu2.enqueue(instruction_2)
        else:
            pass

    def alu3(self):
        if len(self.r_pre_alu3.buffer) > 0:
            instruction_3 = self.r_pre_alu3.dequeue()
            if instruction_3.type == "and":
                instruction_3.temp_ans = self.register_stack[instruction_3.source_1] & self.register_stack[instruction_3.source_2]
            elif instruction_3.type == "or":
                instruction_3.temp_ans = self.register_stack[instruction_3.source_1] | self.register_stack[instruction_3.source_2]
            elif instruction_3.type == "andi":
                instruction_3.temp_ans = self.register_stack[instruction_3.source_1] & instruction_3.immediate
            elif instruction_3.type == "ori":
                instruction_3.temp_ans = self.register_stack[instruction_3.source_1] | instruction_3.immediate
            elif instruction_3.type == "sll":
                instruction_3.temp_ans = self.register_stack[instruction_3.source_1] << instruction_3.immediate
            elif instruction_3.type == "sra":
                instruction_3.temp_ans = self.register_stack[instruction_3.source_1] >> instruction_3.immediate

            if len(self.l_post_alu3.buffer) < self.l_post_alu3.size:
                self.l_post_alu3.enqueue(instruction_3)
        else:
            pass

    def mem(self):
        if len(self.r_pre_mem.buffer) > 0:
            instruction = self.r_pre_mem.dequeue()
            if instruction.type == "sw":
                self.memory_stack[instruction.immediate + self.register_stack[instruction.source_2]] = self.register_stack[instruction.source_1]
                self.remove_active(instruction)
                # self.l_post_mem.enqueue(instruction)
            elif instruction.type == "lw":
                self.l_post_mem.enqueue(instruction)
            else:
                pass
        else:
            pass
        # instruction = self.r_pre_mem.dequeue()

    def wb(self):
        if len(self.r_post_mem.buffer) > 0:
            instruction_1 = self.r_post_mem.dequeue()
            if instruction_1.type == "lw":
                self.register_stack[instruction_1.destination] = instruction_1.temp_ans
                self.remove_active(instruction_1)
        if len(self.r_post_alu2.buffer) > 0:
            instruction_2 = self.r_post_alu2.dequeue()
            self.register_stack[instruction_2.destination] = instruction_2.temp_ans
            self.remove_active(instruction_2)
        if len(self.r_post_alu3.buffer) > 0:
            instruction_3 = self.r_post_alu3.dequeue()
            self.register_stack[instruction_3.destination] = instruction_3.temp_ans
            self.remove_active(instruction_3)
        # for i in range(len(self.l_pre_issue.buffer)):
        #     self.r_pre_issue.enqueue(self.l_pre_issue.dequeue())
        if(len(self.l_pre_issue.buffer) != 0):
            self.r_pre_issue.buffer.extend(self.l_pre_issue.buffer)
            self.l_pre_issue = Buffer(4)
        if(len(self.l_pre_alu1.buffer) > 0):
            self.r_pre_alu1.enqueue(self.l_pre_alu1.dequeue())
        if(len(self.l_pre_alu2.buffer) > 0):
            self.r_pre_alu2.enqueue(self.l_pre_alu2.dequeue())
        if(len(self.l_pre_alu3.buffer) > 0):
            self.r_pre_alu3.enqueue(self.l_pre_alu3.dequeue())
        if(len(self.l_pre_mem.buffer) > 0):
            self.r_pre_mem.enqueue(self.l_pre_mem.dequeue())
        if(len(self.l_post_alu2.buffer) > 0):
            self.r_post_alu2.enqueue(self.l_post_alu2.dequeue())
        if(len(self.l_post_alu3.buffer) > 0):
            self.r_post_alu3.enqueue(self.l_post_alu3.dequeue())
        if(len(self.l_post_mem.buffer) > 0):
            self.r_post_mem.enqueue(self.l_post_mem.dequeue())

        #To change Active status of the instructions
        #delete that instruction from the list of all active instructions 

def pipelining(processor):
    with open('simulation.txt', 'w') as f:
        processor.cycle = 1
        while not processor.stop:
            processor.fetch()
            processor.issue()
            processor.alu1()
            processor.alu2()
            processor.alu3()
            processor.mem()
            processor.wb()
            processor.print_snapshot(f)
            processor.cycle += 1
        # processor.print_snapshot(f)
        # print(processor.program_counter)



def disassembly(processor):
    f = open(sys.argv[1], 'r')
    f_dis = open('disassembly.txt','w')
    temp_break_flag = False
    temp_instruction_counter = 256

    for bin in f.readlines():
        bin = bin.strip()

        if (temp_break_flag):
            f_dis.write(bin+"\t"+str(temp_instruction_counter)+"\t"+str(twos_complement_to_decimal(bin))+"\n")
            processor.memory_stack[temp_instruction_counter] = twos_complement_to_decimal(bin)
        else:
            instruction = Instruction(bin)
            f_dis.write(bin+"\t"+str(temp_instruction_counter)+"\t"+instruction.inst_print+"\n")
            instruction.inst_count = temp_instruction_counter
            processor.instruction_stack[temp_instruction_counter] = instruction.inst_print
            if instruction.type == "break":
                processor.break_instruction_count = temp_instruction_counter
                temp_break_flag = True
        # processor.all_instructions[temp_instruction_counter] = instruction
        processor.all_instructions[temp_instruction_counter] = bin
        temp_instruction_counter += 4
        
    f.close()
    f_dis.close()
    
        
if __name__=="__main__":
    processor = Processing()
    disassembly(processor)
    pipelining(processor)
