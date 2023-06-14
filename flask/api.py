import json
import requests

class API():
    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint

    # -----------------------------------------------------------------------
    # API request functions

    def get_response(self, params=[]):
        """ Sends a request to Azure-function and returns the response
        """
        if 'path' in params.keys():
            path = params['path']
            del(params['path'])
        else:
            path = ''

        api_endpoint = self.endpoint + path
        return requests.get(api_endpoint, params=params)

    def get_json(self, params=[]):
        """ Returns the response from Azure-function in json format
        """
        res = self.get_response(params)
        return json.loads(res.text)

    # -----------------------------------------------------------------------
    # mixed information

    def summary(self):
        """ Returns the summary of the data
        """
        return self.get_json({"type":"summary"})
    
    def get(self, key: str):
        """ Returns n_items, n_groups, n_users, n_clicked_items, n_clicked_groups
            usage : api.get('n_items')
        """
        return self.get_json({"type":"summary", "key": key})

    # -----------------------------------------------------------------------
    # articles

    def popular_articles(self, category_id = None):
        """ Returns the popular articles in a category or in general
        """
        if category_id is not None:
            return self.get_json({"type": "popular_items", "group_id": category_id})
            
        return self.get_json({"type": "popular_items"})

    def random_articles(self, category_id = None):
        """ Returns random articles in a category or in general
        """
        # todo -- return random items from a category
        if category_id is not None:
            return self.get_json({"type": "random_items", "group_id": category_id})

        return self.get_json({"type": "random_items"})

    def recommended_articles(self, article_id = None, user_id = None):
        """ Returns recommended articles with respect to an article or a user
        """
        # recommended items based upon a given item
        if article_id is not None:
            main_item = self.get_json({"type": "details", "item_id": article_id})
            items = self.get_json({"type": "recommended_items", "item_id": article_id})
            items.insert(0, main_item)
            return items
        
        if user_id is not None:
            return self.get_json({"type": "recommended_items", "user_id": user_id})
        
        return self.popular_articles()
    
    def recent_articles(self, category_id = None, user_id = None):
        """ Returns recent articles in general, of a category or of a user
        """
        if category_id is not None:
            return self.get_json({"type": "recent_items", "group_id": category_id})

        if user_id is not None:
            return self.get_json({"type": "recent_items", "user_id": user_id})
        
        return self.get_json({"type": "recent_items"})

    # -----------------------------------------------------------------------
    # categories

    def popular_categories(self):
        """ Returns the popular categories
        """
        return self.get_json({"type": "popular_groups"})

    def random_categories(self):
        """ Returns random categories
        """
        return self.get_json({"type": "random_groups"})

