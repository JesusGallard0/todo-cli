import sqlite3
from datetime import datetime,date ,timedelta
import os
import textwrap
import sys
conexion = sqlite3.connect("todolist.db")
cursor = conexion.cursor() 
conexion.execute("PRAGMA foreign_keys = ON")


def typing_todos ():
    todo = input("Whats on yo mind? :").strip()
    if todo == "":
        print("It has to be called someway dude")
        return
    days = input("what days u wanna do dat?:\n""1.Monday\n""2.Tuesday\n""3.Wednesday\n""4.Thursday\n""5.Friday\n""6.Saturday\n""7.Sunday\n""Enter numbers separated by commas: " ).strip()
    if days == "":
        print("U gotta choose at least one day")
        return
    try:
        day_list = [int(d) for d in days.split(",")]
    except:
        print("Invalid input.")
        return    
    for d in day_list:
        if d < 1 or d > 7:
            print("Days must be between 1 and 7.")
            return
    cursor.execute("""
        INSERT INTO todolist (name,days) VALUES (?,?)""" ,(todo,days) 
)
     
    
    
    
    conexion.commit()
    print("Todo added.")
    
def last_done():
    cursor.execute("""
        SELECT todolist.name, checks.date
        FROM todolist
        LEFT JOIN checks
        ON todolist.id = checks.todo_id
        ORDER BY todolist.id
        """)
    todos = cursor.fetchall()
    for name,date_done in todos:
        print(f"{name}| last done: {date_done}")   
    
    
    
    
def today_todos():
    today = date.today()
    today_number = today.weekday()+1
    cursor.execute("SELECT id,name,days,streak FROM todolist")
    todos = cursor.fetchall()
    print ("\nThis is what u got for today\n")    
    found = False
    todays_ids = []
    for todo in todos:
        todo_id, name, days, streak = todo
        day_list = [int(d) for d in days.split(",")]
        
        cursor.execute("SELECT date FROM checks WHERE todo_id = ?",(todo_id,))
        checks = [datetime.strptime(c[0], "%Y-%m-%d").date() for c in cursor.fetchall()]
        
        skipped = 0
        if checks:
            last_check=max(checks)
        else:
            last_check = None
            
        date_cursor = last_check + timedelta(days=1) if last_check else today
        while date_cursor <= today:
            weekday = date_cursor.weekday() + 1
            if weekday in day_list and date_cursor not in checks:
                skipped += 1
            date_cursor += timedelta(days=1)
        
        if today_number in day_list:
            # Revisar si ya se hizo hoy
            cursor.execute("SELECT * FROM checks WHERE todo_id = ? AND date = ?", (todo_id, today.isoformat()))
            already_checked = cursor.fetchone()
            status = f"streak: {streak}"
            if skipped > 0:
                status += f" | skipped: {skipped}"
            if already_checked:
                status += " ✅ done"
            print(f"{todo_id}) {name} | {status}")
            todays_ids.append(todo_id)
            found = True

    if not found:
        print("Nothing scheduled for today")

    return todays_ids
            
def see_todos():
    cursor.execute(" SELECT id, name, days, streak FROM todolist")
    todos = cursor.fetchall()  
    if not todos :
        print("Nothing yet")
        return
    print("\nYour todos:\n")
    for todo_id, name, days, streak, in todos:
        print(f"{todo_id}) {name} | days: {days} | streak: {streak}" )
      
    #gotta edit days of the todo too
def change_days(): 
    see_todos()
    what = input ("Which todo are u chosing to change the days?: ")
        
    if not what.isdigit():
        print ("Invalid ID")
        return
    todo_id = int(what)
    cursor.execute("SELECT * FROM todolist WHERE id = ? ", (todo_id,))
    todo = cursor.fetchone()
    
    if not todo:
        print("it doesnt exist")
        return
    days_str = todo[2]
    days_list =[int(d) for d in days_str.split(",")]
    
    print(f"\nCurrent days: {days_list}")
    print("1) Add days")
    print("2) Remove days")
    
    action = input("What u wanna do: ").strip()
    
    if action not in ("1","2"):
        print("Invalid option")
        return
    
    change = input(
        "Enter day numbers (1-7) separated by commas:").strip()
    
    try:
        change_days = [int(d) for d in change.split(",")]
    except:
        print("Invalid input")
        return
    
    for d in change_days:
        if d < 1 or d > 7 :
            print("Days must be betweem 1 and 7")
               
            return
        
    if action == "1":
        for d in change_days:
            if d not in days_list:
                days_list.append(d)
    
    elif action == "2":
        for d in change_days:
            if d in days_list:
                days_list.remove(d)
                
        if not days_list :
            print("A todo must have at least one day")
            return        
    
    days_list.sort()
    new_days = ",".join(str(d) for d in days_list)
    cursor.execute("UPDATE todolist SET days = ? WHERE id = ?",(new_days,todo_id)
    )
    conexion.commit()
    print("Days updated succesfully")
        
        
        
        
        
        #this gotta check whats for today,if the app
    #makes sure whats going on today then it 
    #allows you to mark it as done,make sure 
    #it just can happen one time,and once its
    #marked theres no turn back, and its added 
    #to the streak as one more day JUST IN THAT ONLY ONE TO_DO 
    #make sure you cant check any other day and
    #ask 2 times if u sure u wanna mark that as done
    #idk if u should just like press enter to mark as done,or ,literally 
    #typing done to marke it as done
def check_todo(): #MAKE SURE U CANT CHECK MORE THAN ONCE THE SAME DAY
    todays = today_todos()
    if not todays:
        return
    choice = input("\nSelect todo id to mark it as done:").strip()
    if not choice.isdigit() or int(choice) not in todays :
        print("Invalid Selection")
        return
    todo_id = int(choice)
    today_str = date.today().isoformat()
    
    cursor.execute("SELECT* FROM checks WHERE todo_id = ? AND date = ?",(todo_id, today_str))
    if cursor.fetchone():
        print("Aldeady checked today!")
        return
    
    confirm = input("are u sure,cant be undone y/n").strip().lower()
    if confirm not in ("y", "n"):
        print("Invalid option.")
        return
    elif confirm == "n":
        return 
    
    
    elif confirm == "y":
        #this has to save the streak + 1
        cursor.execute("INSERT INTO checks (todo_id, date) VALUES (?, ?)", (todo_id, today_str))
        cursor.execute(
            "UPDATE todolist SET streak = streak + 1 WHERE id = ? ",(todo_id,)
        )
        conexion.commit()
        print("Congratulations u are really raising as a better ")
        
def ver_streak():
    cursor.execute(
        "SELECT name, streak FROM todolist")
    todos = cursor.fetchall()
    print ("\nYour streaks\n")
    for name, streak in todos:
        print(f"{name }: {streak} days")


  #On here we gotta make sure that the user
    #types tha number id,it has to exist and 
    #to be an existing todo and has to make sure if the user wanna dlete  
        
def delete_to_do():
    see_todos()
    choice = input ("What u wanna stop doin?").strip()
    
    if not choice.isdigit():
        print ("Invalid ID")
        return
    todo_id = int(choice)
    cursor.execute("SELECT * FROM todolist WHERE id = ? ", (todo_id,))
    todo = cursor.fetchone()
    
    if not todo:
        print("it doesnt exist")
        return
    confirm =input("U sure ? y/n : ").strip().lower()
    
    if confirm == "y":
        cursor.execute("DELETE FROM todolist WHERE id = ?",(todo_id,))
        conexion.commit()
        print("todo deleted")
    elif confirm == "n":
        print("cancelled")
        return
    elif confirm != ("y","n"):
        print("Im askin u something dude")
        
while True:
    ver_streak()
    today_todos()
    
    print("\nOptions:")
    print("1) Check todo")
    print("2) Add todo")
    print("3)Edit a todo")
    print("4)See last time of everything")
    print("5) Exit")
    
    choice = input("Tryna do sum?: ").strip()
    if choice == "1":
        check_todo()
    
    elif choice == "2":
        typing_todos()
        
    elif choice == "3":
        print("Here u can change the days of ur todo or even delete it")
        udo= input ("what u tryna do?: \n""1)Change days\n""2)Delete a todo")
        
        if udo not in ("1","2"):
            print("invalid input")
            continue
        elif udo == "1":
            change_days()
        elif udo == "2":
            delete_to_do()
    elif choice == "4":
        last_done()
    elif choice == "5":
        break

           
        
        