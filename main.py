from environment import OMDB_API_KEY

from movie_storage_sql import list_movies, delete_movie, update_movie, add_movie_with_api, stats_movies_new, random_movie, search_movie, sorted_movies

def main():
    headline_start()
    while True:
        choice = menu()
        if choice == "1":
            list_movies()
        elif choice == "2":
            user_add_movie()
        elif choice == "3":
            user_delete_movie()
        elif choice == "4":
            user_update_movie()
        elif choice == "5":
            stats_movies_new()
        elif choice == "6":
            random_movie()
        elif choice == "7":
            search_movie()
        elif choice == "8":
            sorted_movies()
        elif choice == "9":
            print("end")
            break


def user_add_movie():
    title = str(input("Enter a movie title to add all informations to the databank - by magic **#*+#* :" )).strip()
    if not title:
        print("No title, sorry!")
        return
    try:
        movie = add_movie_with_api(title, api_key=OMDB_API_KEY)
        print(f"safed: {movie['title']} ({movie['year']}), Rating={movie['rating']}")
    except Exception as e:
        print(f"no movie found, could not safe: {e}")


def headline_start():
    print("************** My Movies Database ***************")


def user_delete_movie():
    title = input("Enter movie name to delete:").strip()
    if not title:
        print("No title, sorry!")
        return
    try:
        title = delete_movie(title)
        print(f"deleted, incl. all informations.")
    except Exception as e:
        print(f"no movie found, could not delete: {e}")


def user_update_movie():
    title = input("Enter movie name to change rating:").strip()
    rating = input("Enter new rating:").strip()
    if not title:
        print("No title, sorry!")
        return
    try:
        title = update_movie(title, rating)
        print(f"Rating changed: new rating: {rating}")
    except Exception as e:
        print(f"no movie found, could not change rating: {e}")


def menu():
    print("\nMenu:")
    print("1. List movies")
    print("2. Add movies")
    print("3. Delete movies")
    print("4. Update movies")
    print("5. Stats")
    print("6. Random movies")
    print("7. Search movies")
    print("8. Movies sorted by rating")
    print("9. end")
    print()
    choice = input("Enter choice (1-9) :")
    return choice


if __name__ == "__main__":
    main()

