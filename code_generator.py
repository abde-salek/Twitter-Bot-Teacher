import random

def generate_code_snippet(tweet_text=None, concept=None):
    """
    Generate a Flutter/Dart code snippet based on the given concept.
    
    Args:
        tweet_text (str, optional): The text to include in the tweet (not used here, handled by tweet_poster.py).
        concept (str, optional): The Flutter concept to generate a code snippet for. If None, a random concept is chosen.
    
    Returns:
        str: The generated code snippet.
    """
    # List of possible concepts
    concepts = ["button", "text", "container", "image", "listview"]
    
    # If no concept is provided, choose a random one
    if concept is None:
        concept = random.choice(concepts)
    
    # Generate the code snippet based on the concept
    if concept.lower() == "button":
        return '''
    ElevatedButton(
    onPressed: () {},
    child: Text('Click Me'),
    )
    '''
        elif concept.lower() == "text":
            return '''
    Text(
    'Hello, Flutter!',
    style: TextStyle(fontSize: 20),
    )
    '''
        elif concept.lower() == "container":
            return '''
    Container(
    color: Colors.blue,
    padding: EdgeInsets.all(16),
    child: Text('Container Example'),
    )
    '''
        elif concept.lower() == "image":
            return '''
    Image.network(
    'https://example.com/image.jpg',
    width: 100,
    height: 100,
    )
    '''
        elif concept.lower() == "listview":
            return '''
    ListView(
    children: [
        ListTile(title: Text('Item 1')),
        ListTile(title: Text('Item 2')),
    ],
    )
    '''
        else:
            return '''
    Container(
    child: Text('Default Widget'),
    )
    '''