from openai import OpenAI
import json

from secrets_handler import SecretsHandler

class OpenAIHandler:
    """
    A static class to handle all OpenAI API interactions.

    Contains a definition for a static _client_instance. This should only be
    accessed via the `get_client()` function, which will automatically fill
    this field if it does not yet exist. Any other accesses to this instance
    are unsafe and should not be used.
    """

    GPT_MODEL = "gpt-3.5-turbo"
    PROMPT = SecretsHandler.get_gpt_prompt()

    def __init__(self) -> None:
        raise TypeError(
            "OpenAIHandler instances should not be created.",
            "Consider using `get_client()`"
        )

    # A static reference to the OpenAI client
    _client_instance: OpenAI | None = None

    @staticmethod
    def get_client() -> OpenAI:
        """
        Retrieves or creates the OpenAI client instance

        Returns
        -------
        OpenAI
            The static OpenAI client
        """
        if OpenAIHandler._client_instance:
            return OpenAIHandler._client_instance

        return OpenAIHandler._initialize_client()

    @staticmethod
    def _initialize_client() -> OpenAI:
        """
        Initializes the OpenAI client.

        This function should never be called outside of this class. To retrieve
        the client safely, use the `get_client` function.

        Returns
        -------
        OpenAI
            The static OpenAI client
        """
        OpenAIHandler._client_instance = OpenAI(
            api_key=SecretsHandler.get_openai_key()
        )

        return OpenAIHandler._client_instance

    @staticmethod
    def get_response(sanitized_input: str) -> list[str]:
        """
        Retrieves a response from the supplied GPT model given an input.

        This input must be pre-sanitized as it will be given directly to the
        model.

        GPT chat completion is non-deterministic by nature. Meaning, the same
        user input may result in a different genres list. We try to mitigate
        this by providing a `seed` value to the API call, but no guarantees
        are made by the OpenAI documentation:
        https://platform.openai.com/docs/guides/text-generation/reproducible-outputs

        Parameters
        ----------
        sanitized_input: str
            The user input (probably an emotion or a phrase describing one)
            to pass to the GPT model

        Returns
        -------
        list[str]
            A list of genres retrieved via the user's input. Unless GPT messes
            up, this list should contain 5 genres.

        Raises
        ------
        ValueError
            if no response was provided by the OpenAI API,
            if the provided response couldn't be parsed into JSON,
            if the parsed JSON did not contain the `genres` key
        """

        # Retrieve a response from GPT
        client = OpenAIHandler.get_client()
        response = client.chat.completions.create(
            model=OpenAIHandler.GPT_MODEL,
            response_format={"type": "json_object"},
            seed=69,
            messages=[
                {"role": "system", "content": OpenAIHandler.PROMPT},
                {"role": "user", "content": sanitized_input}
            ]
        )

        # Ensure a response was found
        found_content = response.choices[0].message.content
        if not found_content:
            raise ValueError(
                "Something went wrong retrieving a response from GPT. " +
                "No response was provided."
            )

        # Ensure the response is JSON
        try:
            content_json = json.loads(found_content)
        except:
            raise ValueError(
                "Something went wrong retrieving a response from GPT. " +
                "The provided response could not be parsed into JSON."
            )

        # Ensure the JSON contains the genres
        if not "genres" in content_json:
            raise ValueError(
                "Something went wrong retrieving a response from GPT. " +
                f"The parsed JSON {content_json} " +
                "does not contain the `genres` key."
            )

        # Return the genres themselves
        return content_json['genres']