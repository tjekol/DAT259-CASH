; ModuleID = "helloWorld.cash"
target triple = "arm64-apple-darwin23.1.0"
target datalayout = "e-m:o-i64:64-i128:128-n32:64-S128"

define i32 @"main"()
{
entry:
  %".2" = bitcast [14 x i8]* @"str1" to i8*
  %".3" = call i32 (i8*, ...) @"printf"(i8* %".2")
  ret i32 0
}

@"str1" = constant [14 x i8] c"Hello World!\0a\00"
declare i32 @"printf"(i8* %".1", ...)
