/* eslint-disable */
/* tslint:disable */
// @ts-nocheck
/*
 * ---------------------------------------------------------------
 * ## THIS FILE WAS GENERATED VIA SWAGGER-TYPESCRIPT-API        ##
 * ##                                                           ##
 * ## AUTHOR: acacode                                           ##
 * ## SOURCE: https://github.com/acacode/swagger-typescript-api ##
 * ---------------------------------------------------------------
 */

/** AuthData */
export interface AuthData {
  /** Email */
  email: string;
  /** Password */
  password: string;
}

/** CreateDraftRequestBody */
export interface CreateDraftRequestBody {
  /** Draftname */
  draftName: string;
}

/** DraftResponseBody */
export interface DraftResponseBody {
  /** Draftname */
  draftName: string;
  /**
   * Userid
   * @format uuid
   */
  userId: string;
  /**
   * Id
   * @format uuid
   */
  id: string;
  /**
   * Createdat
   * @format date-time
   */
  createdAt: string;
  /**
   * Updatedat
   * @format date-time
   */
  updatedAt: string;
  /** Closedat */
  closedAt: string | null;
}

/** HTTPValidationError */
export interface HTTPValidationError {
  /** Detail */
  detail?: ValidationError[];
}

/** Message */
export interface Message {
  /** Message */
  message: string;
}

/** Token */
export interface Token {
  /** Accesstoken */
  accessToken: string;
  /**
   * Tokentype
   * @default "bearer"
   */
  tokenType?: string;
}

/** UserLogin */
export interface UserLogin {
  /**
   * Email
   * @format email
   */
  email: string;
  /** Password */
  password: string;
}

/** UserRegister */
export interface UserRegister {
  /**
   * Email
   * @format email
   */
  email: string;
  /**
   * Username
   * @minLength 3
   * @maxLength 32
   */
  username: string;
  /**
   * Password
   * @minLength 8
   */
  password: string;
}

/** UserResponse */
export interface UserResponse {
  /**
   * Id
   * @format uuid
   */
  id: string;
  /** Email */
  email: string;
  /** Username */
  username: string;
  /**
   * Createdat
   * @format date-time
   */
  createdAt: string;
  /**
   * Updatedat
   * @format date-time
   */
  updatedAt: string;
}

/** ValidationError */
export interface ValidationError {
  /** Location */
  loc: (string | number)[];
  /** Message */
  msg: string;
  /** Error Type */
  type: string;
}

import type {
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
  HeadersDefaults,
  ResponseType,
} from "axios";
import axios from "axios";

export type QueryParamsType = Record<string | number, any>;

export interface FullRequestParams
  extends Omit<AxiosRequestConfig, "data" | "params" | "url" | "responseType"> {
  /** set parameter to `true` for call `securityWorker` for this request */
  secure?: boolean;
  /** request path */
  path: string;
  /** content type of request body */
  type?: ContentType;
  /** query params */
  query?: QueryParamsType;
  /** format of response (i.e. response.json() -> format: "json") */
  format?: ResponseType;
  /** request body */
  body?: unknown;
}

export type RequestParams = Omit<
  FullRequestParams,
  "body" | "method" | "query" | "path"
>;

export interface ApiConfig<SecurityDataType = unknown>
  extends Omit<AxiosRequestConfig, "data" | "cancelToken"> {
  securityWorker?: (
    securityData: SecurityDataType | null,
  ) => Promise<AxiosRequestConfig | void> | AxiosRequestConfig | void;
  secure?: boolean;
  format?: ResponseType;
}

export enum ContentType {
  Json = "application/json",
  JsonApi = "application/vnd.api+json",
  FormData = "multipart/form-data",
  UrlEncoded = "application/x-www-form-urlencoded",
  Text = "text/plain",
}

export class HttpClient<SecurityDataType = unknown> {
  public instance: AxiosInstance;
  private securityData: SecurityDataType | null = null;
  private securityWorker?: ApiConfig<SecurityDataType>["securityWorker"];
  private secure?: boolean;
  private format?: ResponseType;

  constructor({
    securityWorker,
    secure,
    format,
    ...axiosConfig
  }: ApiConfig<SecurityDataType> = {}) {
    this.instance = axios.create({
      ...axiosConfig,
      baseURL: axiosConfig.baseURL || "",
    });
    this.secure = secure;
    this.format = format;
    this.securityWorker = securityWorker;
  }

  public setSecurityData = (data: SecurityDataType | null) => {
    this.securityData = data;
  };

  protected mergeRequestParams(
    params1: AxiosRequestConfig,
    params2?: AxiosRequestConfig,
  ): AxiosRequestConfig {
    const method = params1.method || (params2 && params2.method);

    return {
      ...this.instance.defaults,
      ...params1,
      ...(params2 || {}),
      headers: {
        ...((method &&
          this.instance.defaults.headers[
            method.toLowerCase() as keyof HeadersDefaults
          ]) ||
          {}),
        ...(params1.headers || {}),
        ...((params2 && params2.headers) || {}),
      },
    };
  }

  protected stringifyFormItem(formItem: unknown) {
    if (typeof formItem === "object" && formItem !== null) {
      return JSON.stringify(formItem);
    } else {
      return `${formItem}`;
    }
  }

  protected createFormData(input: Record<string, unknown>): FormData {
    if (input instanceof FormData) {
      return input;
    }
    return Object.keys(input || {}).reduce((formData, key) => {
      const property = input[key];
      const propertyContent: any[] =
        property instanceof Array ? property : [property];

      for (const formItem of propertyContent) {
        const isFileType = formItem instanceof Blob || formItem instanceof File;
        formData.append(
          key,
          isFileType ? formItem : this.stringifyFormItem(formItem),
        );
      }

      return formData;
    }, new FormData());
  }

  public request = async <T = any, _E = any>({
    secure,
    path,
    type,
    query,
    format,
    body,
    ...params
  }: FullRequestParams): Promise<AxiosResponse<T>> => {
    const secureParams =
      ((typeof secure === "boolean" ? secure : this.secure) &&
        this.securityWorker &&
        (await this.securityWorker(this.securityData))) ||
      {};
    const requestParams = this.mergeRequestParams(params, secureParams);
    const responseFormat = format || this.format || undefined;

    if (
      type === ContentType.FormData &&
      body &&
      body !== null &&
      typeof body === "object"
    ) {
      body = this.createFormData(body as Record<string, unknown>);
    }

    if (
      type === ContentType.Text &&
      body &&
      body !== null &&
      typeof body !== "string"
    ) {
      body = JSON.stringify(body);
    }

    return this.instance.request({
      ...requestParams,
      headers: {
        ...(requestParams.headers || {}),
        ...(type ? { "Content-Type": type } : {}),
      },
      params: query,
      responseType: responseFormat,
      data: body,
      url: path,
    });
  };
}

/**
 * @title FastAPI
 * @version 0.1.0
 */
export class API<
  SecurityDataType extends unknown,
> extends HttpClient<SecurityDataType> {
  api = {
    /**
     * No description
     *
     * @tags Authentication
     * @name RegisterApiV1AuthRegisterPost
     * @summary Register
     * @request POST:/api/v1/auth/register
     */
    registerApiV1AuthRegisterPost: (
      data: UserRegister,
      params: RequestParams = {},
    ) =>
      this.request<UserResponse, HTTPValidationError>({
        path: `/api/v1/auth/register`,
        method: "POST",
        body: data,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @tags Authentication
     * @name LoginApiV1AuthLoginPost
     * @summary Login
     * @request POST:/api/v1/auth/login
     */
    loginApiV1AuthLoginPost: (data: UserLogin, params: RequestParams = {}) =>
      this.request<Token, HTTPValidationError>({
        path: `/api/v1/auth/login`,
        method: "POST",
        body: data,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @tags Authentication
     * @name LogoutApiV1AuthLogoutPost
     * @summary Logout
     * @request POST:/api/v1/auth/logout
     */
    logoutApiV1AuthLogoutPost: (params: RequestParams = {}) =>
      this.request<any, any>({
        path: `/api/v1/auth/logout`,
        method: "POST",
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @tags Authentication
     * @name GetUserMeApiV1AuthMeGet
     * @summary Get User Me
     * @request GET:/api/v1/auth/me
     */
    getUserMeApiV1AuthMeGet: (params: RequestParams = {}) =>
      this.request<UserResponse, any>({
        path: `/api/v1/auth/me`,
        method: "GET",
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name GetAllDraftsApiV1DraftAllGet
     * @summary Get All Drafts
     * @request GET:/api/v1/draft/all
     */
    getAllDraftsApiV1DraftAllGet: (params: RequestParams = {}) =>
      this.request<DraftResponseBody[], any>({
        path: `/api/v1/draft/all`,
        method: "GET",
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name CreateDraftApiV1DraftPost
     * @summary Create Draft
     * @request POST:/api/v1/draft
     */
    createDraftApiV1DraftPost: (
      data: CreateDraftRequestBody,
      params: RequestParams = {},
    ) =>
      this.request<DraftResponseBody, HTTPValidationError>({
        path: `/api/v1/draft`,
        method: "POST",
        body: data,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name GetDraftApiV1DraftDraftIdGet
     * @summary Get Draft
     * @request GET:/api/v1/draft/{draft_id}
     */
    getDraftApiV1DraftDraftIdGet: (
      draftId: string,
      params: RequestParams = {},
    ) =>
      this.request<DraftResponseBody, HTTPValidationError>({
        path: `/api/v1/draft/${draftId}`,
        method: "GET",
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name DeleteDraftApiV1DraftDraftIdDelete
     * @summary Delete Draft
     * @request DELETE:/api/v1/draft/{draft_id}
     */
    deleteDraftApiV1DraftDraftIdDelete: (
      draftId: string,
      params: RequestParams = {},
    ) =>
      this.request<any, HTTPValidationError>({
        path: `/api/v1/draft/${draftId}`,
        method: "DELETE",
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name GetCourseSchemaApiV1AiCourseSchemaDraftIdGet
     * @summary Get Course Schema
     * @request GET:/api/v1/ai/course-schema/{draft_id}
     */
    getCourseSchemaApiV1AiCourseSchemaDraftIdGet: (
      draftId: string,
      params: RequestParams = {},
    ) =>
      this.request<any, HTTPValidationError>({
        path: `/api/v1/ai/course-schema/${draftId}`,
        method: "GET",
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name ExportToLmsApiV1AiExportDraftIdPost
     * @summary Export To Lms
     * @request POST:/api/v1/ai/export/{draft_id}
     */
    exportToLmsApiV1AiExportDraftIdPost: (
      draftId: string,
      data: AuthData,
      params: RequestParams = {},
    ) =>
      this.request<any, HTTPValidationError>({
        path: `/api/v1/ai/export/${draftId}`,
        method: "POST",
        body: data,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name ChatApiV1AiChatDraftIdPost
     * @summary Chat
     * @request POST:/api/v1/ai/chat/{draft_id}
     */
    chatApiV1AiChatDraftIdPost: (
      draftId: string,
      data: Message,
      params: RequestParams = {},
    ) =>
      this.request<any, HTTPValidationError>({
        path: `/api/v1/ai/chat/${draftId}`,
        method: "POST",
        body: data,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name ChatApiV1AiDraftIdGet
     * @summary Chat
     * @request GET:/api/v1/ai/{draft_id}
     */
    chatApiV1AiDraftIdGet: (draftId: string, params: RequestParams = {}) =>
      this.request<any, HTTPValidationError>({
        path: `/api/v1/ai/${draftId}`,
        method: "GET",
        format: "json",
        ...params,
      }),
  };
}
