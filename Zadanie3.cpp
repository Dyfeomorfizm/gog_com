/* Run in console with 2 arguments:
   path to directory &&
   depth - int with 0 means no subdirectories */

#include <windows.h>
#include <string>
#include <vector>
#include <iostream>

using namespace std;

string tabs(int depth, int max_depth)
{
	string tab = "";
	for (int i = depth; i < max_depth; i++)
	{
		tab += "  ";
	}
	return tab;
}

void ListFiles(string path, string mask, int depth, int max_depth, vector<string> &executables) {
    
	HANDLE hFind = INVALID_HANDLE_VALUE;
    WIN32_FIND_DATA ffd;
    string spec;
    string tab;
    DWORD dwBinaryType;
    
    spec = path + "\\" + mask;
    hFind = FindFirstFile(spec.c_str(), &ffd);
    tab = tabs(depth, max_depth);
	    
    do
    {
    	if (strcmp(ffd.cFileName, ".") != 0 && 
            strcmp(ffd.cFileName, "..") != 0)
        {
            if (ffd.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) 
			{
                cout << tab + "|_" << ffd.cFileName << endl;
                if (depth != 0)
                ListFiles(path + "\\" + ffd.cFileName, mask, depth - 1, max_depth, executables);
            }
            else 
			{
                cout<<tab+"|_"<<ffd.cFileName<<endl;
                if (GetBinaryType((path + "\\" + ffd.cFileName).c_str(), &dwBinaryType) )
                {
                	executables.push_back(path + "\\" + ffd.cFileName);
				}
            }            	
		}
	}while (FindNextFile(hFind, &ffd) != 0);
	
	if (GetLastError() != ERROR_NO_MORE_FILES)
	{
        FindClose(hFind);
    }
    FindClose(hFind);
}

int main(int argc, char* argv[])
{
	vector<string> executables;
    
	string p = argv[1];
	int d = atoi(argv[2]);
	
	executables.clear();
	
	
    ListFiles(p, "*", d, d, executables);
    
    cout << endl << "executables:" << endl;
    
    for (vector<string>::iterator it = executables.begin(); 
             it != executables.end(); 
             ++it) {
            cout << it->c_str() << endl;
        }
    
	return 0;
}
