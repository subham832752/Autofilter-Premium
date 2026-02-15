        if user_id is None:
            update_data = {"$set": {"has_free_trial": False}}
            result = await self.users.update_many({}, update_data)  
            return result.modified_count
        else:
            update_data = {"$set": {"has_free_trial": False}}
            result = await self.users.update_one({"id": user_id}, update_data)
            return 1 if result.modified_count > 0 else 0  
        
    async def all_premium_users(self):
        count = await self.users.count_documents({
        "expiry_time": {"$gt": datetime.datetime.now()}
        })
        return count
    
    async def get_bot_setting(self, bot_id, setting_key, default_value):
        bot = await self.botcol.find_one({'id': int(bot_id)}, {setting_key: 1, '_id': 0})
        return bot[setting_key] if bot and setting_key in bot else default_value
        
    async def update_bot_setting(self, bot_id, setting_key, value):
        await self.botcol.update_one(
            {'id': int(bot_id)}, 
            {'$set': {setting_key: value}}, 
            upsert=True
        )

    async def connect_group(self, group_id, user_id):
        user= await self.connection.find_one({'_id': user_id})
        if user:
            if group_id not in user["group_ids"]:
                await self.connection.update_one({'_id': user_id}, {"$push": {"group_ids": group_id}})
        else:
            await self.connection.insert_one({'_id': user_id, 'group_ids': [group_id]})

    async def get_connected_grps(self, user_id):
        user = await self.connection.find_one({'_id': user_id})
        if user:
            return user["group_ids"]
        else:
            return []
        
    async def remove_group_connection(self, group_id, user_id):
        await self.connection.update_one(
            {'_id': user_id},
            {'$pull': {'group_ids': group_id}}
        )

    async def pm_search_status(self, bot_id):
        return await self.get_bot_setting(bot_id, 'PM_SEARCH', PM_SEARCH)

    async def update_pm_search_status(self, bot_id, enable):
        await self.update_bot_setting(bot_id, 'PM_SEARCH', enable)

    async def movie_update_status(self, bot_id):
        return await self.get_bot_setting(bot_id, 'MOVIE_UPDATE_NOTIFICATION', MOVIE_UPDATE_NOTIFICATION)

    async def update_movie_update_status(self, bot_id, enable):
        await self.update_bot_setting(bot_id, 'MOVIE_UPDATE_NOTIFICATION', enable)
     
db = Database(DATABASE_URI, DATABASE_NAME)    
db2 = Database(DATABASE_URI2, DATABASE_NAME)


