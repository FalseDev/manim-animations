#include <stdio.h>

int main() {
    int arr[10]={0,1,2,3};
    int n=4, val=10, pos=1, i;
    n++;
    for (i=n-1;i>pos;i--){
        arr[i]=arr[i-1];
    }
    arr[pos]=val;

    for (i=0;i<n;i++){
        printf("%d\n", arr[i]);
    }
}