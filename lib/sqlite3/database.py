# Standard imports.
import sqlite3   


class SmellyMemory:
        
    def activate(self, channel:int): 
            """ Activate SmellyBot for channel. Database will be created for his memory.
            """   

            conn = sqlite3.connect('smelly_brain.db')
            c = conn.cursor()

            # Create Memory table if doesn't exist.
            c.execute("""CREATE TABLE IF NOT EXISTS Memory (
                        channel int,   
                        memory text    
                        )""")

            # Check to see if channel exists.
            c.execute("SELECT memory FROM Memory WHERE channel = ?", (channel,))
            channel_exists = c.fetchall()
            
            if channel_exists: return ('I am already listening.')
            
            else:            
                c.execute("INSERT INTO Memory (channel) VALUES (?)", (channel,))
                conn.commit()
                conn.close()
                
                return f'''Hey there! It's me... SmellyBot! I will get in on the conversation when i hear smellybot.\n
Shhhhh... it's ok now guys. SmellyBot is here.
                '''
            

    def update_memory(self, channel:int, name:str, content:str):
            """ Add the new message to the existing 'memory string'.
            """

            conn = sqlite3.connect('smelly_brain.db')
            c = conn.cursor()        

            c.execute("SELECT memory FROM Memory WHERE channel = ?", (channel,))
            smelly_memory = c.fetchall()[0][0]
            smelly_first_output = 'SmellyBot:I am SmellyBot.'        

            # After Smellybot is called insert first entry to database.
            if smelly_memory is None:
                c.execute("UPDATE Memory SET memory = ? WHERE channel = ?", (f'{smelly_first_output}-{name}:{content}-', channel))
                conn.commit()
                conn.close()

            # If there is a memory, pull the entire string and append the new content.              
            else:
                c.execute("SELECT memory FROM Memory WHERE channel = ?", (channel,))
                memory_string = c.fetchall()[0][0]
                new_memory_string = f'{memory_string}{name}:{content}-'

                c.execute("UPDATE Memory SET memory = ? WHERE channel = ?", (new_memory_string, channel))
                conn.commit()
                conn.close()
