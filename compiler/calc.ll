; ModuleID = "calc.cash"
target triple = "arm64-apple-darwin23.1.0"
target datalayout = "e-m:o-i64:64-i128:128-n32:64-S128"

define i32 @"main"()
{
entry:
  %".2" = mul i32 15, 2
  %".3" = sub i32 100, 10
  %".4" = mul i32 %".2", %".3"
  %".5" = sdiv i32 %".4", 100
  %".6" = bitcast [11 x i8]* @"str1" to i8*
  %".7" = call i32 (i8*, ...) @"printf"(i8* %".6", i32 %".5")
  ret i32 0
}

@"str1" = constant [11 x i8] c"Total: %d\0a\00"
declare i32 @"printf"(i8* %".1", ...)
