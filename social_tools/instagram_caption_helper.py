def add_niche_hashtags(caption, hashtags=None):
    """
    Aggiunge hashtag di nicchia a una caption Instagram, limitando a 5 tag mirati.
    Se non forniti, usa un set predefinito per fotografia Fuji X100V.
    
    Args:
        caption (str): Testo della caption originale.
        hashtags (list, optional): Lista personalizzata di hashtag. Default: nicchia foto.
    
    Returns:
        str: Caption completa con hashtag aggiunti (max 5).
    """
    # Set di hashtag nicchia per Fuji X100V / street / Firenze (scegli i migliori 5)
    default_hashtags = [
        '#fujix100v', '#streetphotographyitaly', '#florencestreet',
        '#fujifilmitalia', '#x100vstreet', '#minimalstreetphoto',
        '#everydaystreet', '#urbanvibesitalia', '#candidstreet'
    ]
    
    if hashtags is None:
        hashtags = default_hashtags
    
    # Seleziona i primi 5 (o meno se lista più corta)
    selected_hashtags = hashtags[:5]
    
    hashtag_block = ' \\\n'.join(selected_hashtags)
    
    # Aggiungi 2 linee vuote + blocco hashtag
    final_caption = caption.strip() + '\n\n' + hashtag_block
    
    return final_caption

