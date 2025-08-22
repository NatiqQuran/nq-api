import * as TakhtitsType from "../types/takhtits";
import * as WordsType from "../types/words";
import * as AyahsType from "../types/ayahs";
import { AxiosResponse } from "axios";
import { Connection } from "../client/connection";
import { BaseController } from "../utils/baseController";
import { RequestConfig } from "../utils/globalTypes";

export class TakhtitsAyahs_breakers extends BaseController {
    constructor(conn: Connection, token?: string) {
        super(conn, token);
    }
    /** GET /takhtits/{uuid}/ayahs_breakers/ */
    async takhtits_ayahs_breakers_list(uuid: string, config?: RequestConfig
    ): Promise<AxiosResponse<TakhtitsType.TakhtitsAyahs_breakersGetResponseData>> {
        return await this.axiosGet(`/takhtits/${uuid}/ayahs_breakers/`, config);
    }
    /** POST /takhtits/{uuid}/ayahs_breakers/ */
    async takhtits_ayahs_breakers_create(uuid: string, data: TakhtitsType.TakhtitsAyahs_breakersPostRequestData, config?: RequestConfig
    ): Promise<AxiosResponse<TakhtitsType.TakhtitsAyahs_breakersPostResponseData>> {
        return await this.axiosPost(`/takhtits/${uuid}/ayahs_breakers/`, data, config);
    }
}

export class TakhtitsImport extends BaseController {
    constructor(conn: Connection, token?: string) {
        super(conn, token);
    }
    /** POST /takhtits/{uuid}/import/ */
    async takhtits_import_create(uuid: string, config?: RequestConfig<TakhtitsType.TakhtitsImportRequestParams>
    ): Promise<AxiosResponse<TakhtitsType.TakhtitsImportPostResponseData>> {
        return await this.axiosPost(`/takhtits/${uuid}/import/`, config);
    }
}

export class TakhtitsWords_breakers extends BaseController {
    constructor(conn: Connection, token?: string) {
        super(conn, token);
    }
    /** GET /takhtits/{uuid}/words_breakers/ */
    async takhtits_words_breakers_list(uuid: string, config?: RequestConfig
    ): Promise<AxiosResponse<TakhtitsType.TakhtitsWords_breakersGetResponseData>> {
        return await this.axiosGet(`/takhtits/${uuid}/words_breakers/`, config);
    }
    /** POST /takhtits/{uuid}/words_breakers/ */
    async takhtits_words_breakers_create(uuid: string, data: TakhtitsType.TakhtitsWords_breakersPostRequestData, config?: RequestConfig
    ): Promise<AxiosResponse<TakhtitsType.TakhtitsWords_breakersPostResponseData>> {
        return await this.axiosPost(`/takhtits/${uuid}/words_breakers/`, data, config);
    }
}
export class TakhtitsAyahs_breakersResource extends BaseController {
    constructor(conn: Connection, token?: string) {
        super(conn, token);
    }
    /** GET /takhtits/{uuid}/ayahs_breakers/{breaker_uuid}/ */
    async takhtits_ayahs_breakers_retrieve(uuid: string, breaker_uuid: string, config?: RequestConfig
    ): Promise<AxiosResponse<TakhtitsType.TakhtitsAyahs_breakersResourceGetResponseData>> {
        return await this.axiosGet(`/takhtits/${uuid}/ayahs_breakers/${breaker_uuid}/`, config);
    }
}
export class TakhtitsWords_breakersResource extends BaseController {
    constructor(conn: Connection, token?: string) {
        super(conn, token);
    }
    /** GET /takhtits/{uuid}/words_breakers/{breaker_uuid}/ */
    async takhtits_words_breakers_retrieve(uuid: string, breaker_uuid: string, config?: RequestConfig
    ): Promise<AxiosResponse<TakhtitsType.TakhtitsWords_breakersResourceGetResponseData>> {
        return await this.axiosGet(`/takhtits/${uuid}/words_breakers/${breaker_uuid}/`, config);
    }
}

export class TakhtitsController extends BaseController {
    public readonly ayahs_breakers: TakhtitsAyahs_breakers;
    public readonly import: TakhtitsImport;
    public readonly words_breakers: TakhtitsWords_breakers;
    public readonly ayahs_breakers_resource: TakhtitsAyahs_breakersResource;
    public readonly words_breakers_resource: TakhtitsWords_breakersResource;

    constructor(connection: Connection, token?: string) {
        super(connection, token);
        this.ayahs_breakers = new TakhtitsAyahs_breakers(this.conn);
        this.import = new TakhtitsImport(this.conn);
        this.words_breakers = new TakhtitsWords_breakers(this.conn);
        this.ayahs_breakers_resource = new TakhtitsAyahs_breakersResource(this.conn);
        this.words_breakers_resource = new TakhtitsWords_breakersResource(this.conn);
    }
    
    /** GET /takhtits/ */
    async list(config?: RequestConfig<TakhtitsType.TakhtitsListRequestParams>
    ): Promise<AxiosResponse<TakhtitsType.TakhtitsListResponseData>> {
        return await this.axiosGet(`/takhtits/`, config);
    }
    
    /** POST /takhtits/ */
    async create(data: TakhtitsType.TakhtitsCreateRequestData, config?: RequestConfig
    ): Promise<AxiosResponse<TakhtitsType.TakhtitsCreateResponseData>> {
        return await this.axiosPost(`/takhtits/`, data, config);
    }
    
    /** GET /takhtits/{uuid}/ */
    async retrieve(uuid: string, config?: RequestConfig
    ): Promise<AxiosResponse<TakhtitsType.TakhtitsRetrieveResponseData>> {
        return await this.axiosGet(`/takhtits/${uuid}/`, config);
    }
    
    /** PUT /takhtits/{uuid}/ */
    async update(uuid: string, data: TakhtitsType.TakhtitsUpdateRequestData, config?: RequestConfig
    ): Promise<AxiosResponse<TakhtitsType.TakhtitsUpdateResponseData>> {
        return await this.axiosPut(`/takhtits/${uuid}/`, data, config);
    }
    
    /** PATCH /takhtits/{uuid}/ */
    async partialUpdate(uuid: string, data: TakhtitsType.TakhtitsPartialupdateRequestData, config?: RequestConfig
    ): Promise<AxiosResponse<TakhtitsType.TakhtitsPartialupdateResponseData>> {
        return await this.axiosPatch(`/takhtits/${uuid}/`, data, config);
    }
    
    /** DELETE /takhtits/{uuid}/ */
    async delete(uuid: string, config?: RequestConfig
    ): Promise<AxiosResponse<any>> {
        return await this.axiosDelete(`/takhtits/${uuid}/`, config);
    }
    
}