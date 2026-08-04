from database.supabase import supabase


def find_offices(department, district):
    """
    Search offices by department and district.
    """

    if supabase is None:
        return []

    try:

        response = (
            supabase
            .table("offices")
            .select("*")
            .ilike("department", f"%{department}%")
            .ilike("district", f"%{district}%")
            .execute()
        )

        return response.data

    except Exception as e:

        print(e)

        return []
