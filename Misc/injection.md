# Injection Techniques

Hello there this goes a little in-depth into the 5 (+2) injectioin techniques (technically hollowing is not a  *injection* technique)

![hyewon](./Assets/hyewon.gif)

## Menu
- [Injection Techniques](#injection-techniques)
  - [Menu](#menu)
- [_____________________________________________________](#_____________________________________________________)
  - [0. Prelude](#0-prelude)
  - [1. Classical DLL injection](#1-classical-dll-injection)
  - [2. Reflective dll injection](#2-reflective-dll-injection)
  - [3. PE injection](#3-pe-injection)
  - [4. Process Hollowing](#4-process-hollowing)
  - [5. Thread Hijack](#5-thread-hijack)
  - [6. Hook Injection via SetWindowsHookEx](#6-hook-injection-via-setwindowshookex)
- [Summary](#summary)
- [Conclusion](#conclusion)
   
# _____________________________________________________

## 0. Prelude 

I will assume you know what these means:
* what happen when a dll is loaded into a process
* Linking, Loading
* Disk, Memory
* BaseImageAddress

## 1. Classical DLL injection

Instead of explaining the function in a chronological/sequential order, I will explain in the thought process order, from the malware author POV. So how does it all begin with a dll injection? 

Assuming you have managed to drop a malicious dll into the host system, and now we need to _force_ one process to run this dll (for stealth reasons). How can we do this? 

First we need to find a process:
```
CreateToolhelp32Snapshot
Process32First
Process32Next

# Those will iterate through the pids, but we need the handle so

OpenProcess(arg1,arg2,pid)
# which will return handle of the process  
```

After that we will need to force this process to run what we need. But how? 

The answer is *CreateRemoteThread*, which \"creates a thread that runs in the virtual address space of another process\". Please look at the [MSDN](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createremotethread) carefully. 

```
CreateRemoteThread(hProcess, NULL, 0, (LPTHREAD_START_ROUTINE), lpStartAddress, lpBaseAddress, 0, NULL);
```

We want to let the victim process run the dll, so that takes two steps:
* Make the thread routine do a run-dll-subroutine in the lpStartAddress argument: "A pointer to the application-defined function of type LPTHREAD_START_ROUTINE to be executed by the thread and represents the starting address of the thread in the remote process. The function must exist in the remote process"
* Pass the appropriate arguments into this subroutine: lpParameter. A pointer to a variable to be passed to the thread function. Needless to say, this argument must exist inside the remote process (victim) address space. 

For the first part of the puzzle, we can run the dll by calling *LoadLibraryA*

```
HMODULE hModule = GetModuleHandle("kernel32.dll"); #get kernel32.dll

LPVOID lpStartAddress = GetProcAddress(hModule, "LoadLibraryA"); #get LoadLibraryA inside kernel32.dll
```

So we just need to pass the address of LoadLibraryA to CreateRemoteThread. Sincee LoadLibraryA comes from kernel32.dll, its address is viewed similarly from all processes that want to import it. We can just import LoadLibraryA in our own malware process, then pass the lpStartAdress to CreateRemoteThread. The hProcess will be able to run LoadLibraryA. 

Most functions will have loadlibraryA address in it (otherwise, it doesn't rely on any dll... abit far fetch). Anyway you can just verify that the victim process uses LoadLibraryA, which a lot of default processes in the computer do. 

Now the second part of the puzzle is how do we pass the arguments of CreateRemoteThread, in this case, is the fullpath of our dll into the subroutine. Because the remote process will NOT have this malicious string inside itself. So how?

**_We will need to write this string (fullpath to dll) into the victim process._** 

This will be done via the combination of VirtualAllocEx and WriteProcessMemory. 

```
LPVOID lpBaseAddress = VirtualAllocEx(hProcess, NULL, dwDllPathLen, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);

WriteProcessMemory(hProcess, lpBaseAddress, lpszDllPath, dwDllPathLen, &dwWritten);

```

Looking at MSDN of VirtualAllocEx 
* If lpAddress is NULL, the function determines where to allocate the region. 
* MEM_COMMIT | MEM_RESERVE: refer to MSDN for the details of this memory region. 
* If the pages are being committed, you can specify any one of the memory protection constants.

So in short we can allocate a writeable memory region, and then proceed to write into it with WriteProcessMemory. Why is VirtualAllocEx even exist? I have no idea. [here is some guide on commit and reserver memory](https://flylib.com/books/en/1.563.1.85/1/)

Tying all together, the killchain is:
- Get the process id of the target process via CreateToolhelp32Snapshot, Process32First Process32Next or any other viable means
- Get the handle via *OpenProcess*
- Allocate some memory for the fullpath string of the dll via *VirtualAllocEx* (it is initialized to 0)
- Write the fullpath string into this region via *WriteProcessMemory*
- Get the address of LoadLibraryA via *GetModuleHandle* and *GetProcAddress* 
- *Now we know (1) the dll fullpath string is in the victim process (2) it also have the address of LoadLibraryA loaded in its address space, which we know what it is (safe assumption tbh)
- Call CreateRemoteThread, with LoadLibraryA address and the fullpath string that we wrote earlier. It will now load the dll and be forced to run the dll's mainEntryPoint. Mission Accomplished. 

But it will have a few issues, that we gonna address soon enough

## 2. Reflective dll injection 

As seen from classical dll injection, there is a few issues:
* You need to have a dll in disk to have a fullpath to it
* reliance on LoadLibraryA 

Reflective dll will try to circumvent this by:
* Map the raw binary within its own process into the victim process
* Manually load the dll into the victim 

We can also keep the malicious dll in resource section and extract it via the: 
* FindResouce | LoadResource | SizeOfResource | LockResource

Keep in mind that after calling LockResource, the pointer to the DLL resource is read-only and the data is in its disk form, meaning that the offsets are all file offsets, not memory offsets.

*We need to make the malware into its memory form* 

This is done via:
  * MapViewOfFIle to create a memory region: maps a view of a file mapping into the address space of a calling process.
  * CopyMemory to copy all the sections of the file into the address space
  * UnMapViewOfFile 

This is essentially similar to bringing file from disk to RAM. 

So now the DLL is in memory, we need to allocate enough space for the entire dll to be put inside the target process:
* Find the process as classical dll 
* VirtualAllocEx the entire dll in with VirtualAllocEx(this->payload->hProcess, NULL, **pinh->OptionalHeader.SizeOfImage**, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE)

After the allocation is done:
* rebuild Import Address Table (IAT) by walking through the IAT, get the dll name we need then call GetProcAddress and rewrite the value into FirstThunk 
* rebuild the relocation table via: 
  * dwDelta = reinterpret_cast<DWORD>(this->payload->lpAddress) - pinh->OptionalHeader.ImageBase; #offset between victim process and the current process
  * _since the address in the dll reloc table is all from the dll memory space, but now we are mapping it to the victim process, all these addresses need to conform to the victim process._
  * walk through the entry of reloc table, apply the offset. 

Now we have the newly rebuilt dll and all of its addresses have been rebuilt such that it looks like it has been living in the victim process its whole life (all of its reloc entries is derived from the victim process BaseImageAddress). Proceed to WriteProcessMemory the entire binary into the VirtualAllocEx region. 

Now we just need to call the dllMainEntry, as the dll is already loaded into the process memory. 

So compare to classical dll:
* Instead of forcing the process to call LoadLibraryA, we do the loading ourself via Extract the dll into disk form >> Map it to Memory >> (if VirutalAllocEx succeeds) Fix the IAT and reloc Table >> Write the raw binary into the process
* Does not need any fullpath
* The dll does not need to be on disk

## 3. PE injection

Similar to Reflective dll, we create a memory block of size ImageSize. The thing is instead of a dll, we gonna copy the whole malware PE into the process (which is actually ok because malware is only 1-2kB). The steps gonna be similar to refelctive:
* Instead of extracting the dll from rsrc, we copy the whole malware PE file into the memory region (most likely systenm heap) via VirtualAlloc
* Find process, and VirtualAllocEx the ntHeader->OptionalHeader.SizeOfImage
* Fix the IAT and Reloc Table:
  * There is a slight detail to notice here: patchedAddress = (PDWORD_PTR)((DWORD_PTR)localImage + relocationTable->VirtualAddress + relocationRVA\[i\].Offset); 
  * In assembly, you will see 2 for loops (2 while, while for, for while, 2 for) with **0x0fff** used to access the relocationRVA\[i\].Offset 
* Copy the whole PE into the victim process. The PE now lives inside the victim process
* Call CreateRemoteThread and set the lpStartAddress into the entry point of the malicious subroutine inside the PE.

## 4. Process Hollowing

For the sake of terminology, we shouldn't call hollowing an injection technique because it is not "injecting" things into a live process. Instead it creates a zombie process by CreateProcess in suspended mode (Process Creation Flag = 0x04). It will then hollow out the victim process with UnMapViewofSection. See this animation for better visualization

![Hollowing](https://gblobscdn.gitbook.com/assets%2F-LFEMnER3fywgFHoroYn%2F-LdZYWVJBogQAobjsEcY%2F-LdZdqi5lVWlRdAX4Ibx%2FPeek%202019-04-28%2016-53.gif?alt=media&token=44f6cd64-7ae5-4216-a9ad-c38f72c97415)

Credit: ired team 

As you can see, the victim process is now hollowed out. After that we will use VirtualAllocEx (there is a slight implementation caveat mentioned by ired team, where we would like to specify the memory region allocated by VirtualAllocEx to be at BaseImageAddress of the hollowed process. However they eencounter ERROR_INVALID_ADDRESS due to enclave? ) 

Anyway the next step after VirtualAllocEx succeed is to WriteProcessMemory. It can write shellcode, write LoadLibraryA(fullpath_to_dll), or the loaded dll. 

![ hollow](https://gblobscdn.gitbook.com/assets%2F-LFEMnER3fywgFHoroYn%2F-LdZf3DPrfIUuLWOgj2E%2F-LdZi9x5PFAt0n39KYBj%2FPeek%202019-04-28%2017-12.gif?alt=media&token=5c106680-b0c7-4782-b154-18446dea26ab)
Credit: ired team

Then **SetThreadContext** to change the entry point (AddressOfEntryPoint in the eax register in the current victim thread context). So we need to get the context via **GetThreadContext**, patch the context->eax to the new entry point, then **SetThreadContext**.

And voila ResumeThread.

## 5. Thread Hijack

Same thing, but with thread. I will need to force the thread to run my dll/shellcode/etc. So again I will need to write something to it (VirtualAllocEx + WriteProcessMemory combo), and force it to run a subroutine (shell, loaded dll, LoadLibraryA(fullpath to dll) ) that I just wrote. This can be done via (GetThreadContext + SetThreadContext combo) to reset the AddressOfEntryPoint and then call resumeThread. 

So all that's left is to find a process and then suspend it. 

Killchain:
* Find target thread (Snapshot,T32First, T32Next). 
* Suspend it via SuspendThread. 
* VirtualAllocEx + WriteProcessMemory to write stuff
* GetThreadContext + SetThreadContext to reset the AddressOfEntryPoint
* Resume Thread

It is similar to Hollowing in these regards:
* the Suspend (here we find a live thread and suspend it vs Hollowing start a thread in suspended mode)
* the change of AddressOfEntryPoint (GetThreadContext + SetThreadContext)
* Resume Thread

The difference is there is no unmap aka the original process is not wiped out of memory. 

## 6. Hook Injection via SetWindowsHookEx 

This is an interesting technique that took me sometimes (and online demo) to understand. 

First thing, SetWindowsHookEx allow an user defined interrupt to be called upon the trigger of an event. The last argument can be set to 0, which will make the hook a _global hook_, aka any thread/process can be hooked if performing the action. For e.g, if I set the hook type to be Keyboard, the routine to be called _meow\_somemore()_ and set 0 to last argument of SetWindowsHookEx, _**any process/thread that needs a key press will need to run meow\_somemore()**_. 

Now read [this article](https://resources.infosecinstitute.com/topic/using-setwindowshookex-for-dll-injection-on-windows/)

To recap the article: the malware install the meconnect function in the malicious dll into the WH_KEYBOARD hook. Every process that uses a keypad (for e.g, notepad) will then have to load the malicious dll into its address space, and then do whatever meconnect do. 

A very concise code has been done by [ired team](https://www.ired.team/offensive-security/code-injection-process-injection/setwindowhookex-code-injection).

Of course as usual, creating a global hook is a noisy process. So the dll should be wary of which process is using the hook and only target the desirable ones. See [example](https://warroom.rsmus.com/dll-injection-part-1-setwindowshookex/)



# Summary

The signature of each methods are:
* Classic: find process using (Snapshot,P32First, P32Next combo) >> VirtualAllocEx + WriteProcessMemory >> CreateRemoteThread (which call LoadlibraryA)
* Reflective: find process >> VirtualAllocEx + WriteProcessMemory in a nested for loop with relocationRVA\[i\].offset (0x0fff in assembly) >> CreateRemoteThread
* PE: Same as Reflective but for a PE file 
* Hollowing: **No find process** BUT Create Suspended Process >> Unmap >> VirtualAllocEx + WriteProcessMemory in nested for loop (aka base relocation routine)>> GetThreadContext + SetThreadContext >> ResumeThread
* Thread Hijack: find target thread (Snapshot,T32First, T32Next) >> VirtualAllocEx + WriteProcessMemory >> GetThreadContext + SetThreadContext >> ResumeThread
* Hook Inject: 

If we define the function as bit order as folowing:
*  SetWindowsHookEx | create process | (first 2 bit)
*  find process combo | find thread combo |  UnmapViewOfFile | MapViewOfFile | (next 4 bits)
*  VirtualAllocEx + WriteMem ONCE | Virtual AllocEx + WriteMem nested for loop (base reloc) | Get OR SetThreadContext + Resume Thread | CreateRemoteThread | (last 4 bits)

Then the hash (similar to imphash) for each method is: 
* Classic | 01 0000 1001 | 0x109
* Reflective | 01 0001 0101 | 0x113
* PE Injection | 01 0000 0101 | 0x103
* Hollowing |  00 1010 0110 | 0x0A6
* Thread Hijack | 00 0100 1110 | 0x04E
* Windows Hook |  10 0000 0000 | 0x200

As you can see that there's a very big overlap between techniques. It's probably easier to identify the API it uses then have a nice guess. 

# Conclusion

Yeet yolo I have seen an unmap function in tutorial 8 - lala.exe (the technique use CreateSection and MapViewOfSection to inject code). 

Oh well... be careful fwans there is MUCH MUCH MUCH MORE (and often UNNAMED techniques) out there. But at least if we see the classics we can identify for now :> 

![what](./Assets/what.gif)

Gone. 






